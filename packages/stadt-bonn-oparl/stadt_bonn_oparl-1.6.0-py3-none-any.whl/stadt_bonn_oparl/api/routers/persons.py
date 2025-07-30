from typing import Optional

import httpx
import logfire
from fastapi import APIRouter, Depends, HTTPException, Query

from stadt_bonn_oparl.api.dependencies import (
    chromadb_persons_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.helpers import _get_person
from stadt_bonn_oparl.api.models import PersonListResponse, PersonResponse

router = APIRouter()


@router.get(
    "/persons", tags=["oparl"], response_model=PersonResponse | PersonListResponse
)
async def persons(
    person_id: Optional[str] = Query(None, alias="id"),
    body_id: Optional[str] = Query(None, alias="body"),
    page: Optional[int] = Query(None, ge=1, le=1000),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_persons_collection),
):
    """Get the persons from the Stadt Bonn OParl API.

    see https://oparl.org/spezifikation/online-ansicht/#entity-person
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/persons"

    # if person_id and body_id is provided, raise an error
    if person_id is not None and body_id is not None:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch person information from OParl API: please provide either id or body, not both.",
        )

    try:
        if person_id is None and body_id is None:
            response = http_client.get(_url)
            if response.status_code == 200:
                return PersonListResponse(**response.json())
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to fetch person information from OParl API",
                )

        if person_id and not body_id:
            _person = await _get_person(http_client, person_id)
            collection.upsert(
                documents=[str(_person)],
                metadatas=[
                    {
                        "id": _person.id,
                        "type": _person.type,
                        "affix": _person.affix,
                        "given_name": _person.givenName,
                        "family_name": _person.familyName,
                        "name": _person.name,
                        "gender": _person.gender,
                        "status": str(_person.status),
                    }
                ],
                ids=[_person.id],
            )

            return PersonResponse(**_person.model_dump())

        if body_id:
            # if body_id is provided, we need to fetch all persons for that body
            # if page is provided, we need to fetch the persons for that body
            if page is not None:
                _request = _url + f"?body={body_id}&page={page}"
            else:
                _request = _url + f"?body={body_id}"
            response = http_client.get(_request)
            if response.status_code == 200:
                return PersonListResponse(**response.json())
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed hard to fetch person information from OParl API",
                )
    except Exception as e:
        logfire.error(f"Error fetching person information: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch person {person_id} information from OParl API",
        )
