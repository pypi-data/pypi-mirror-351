from typing import Optional

import httpx
import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger

from stadt_bonn_oparl.api.dependencies import (
    chromadb_organizations_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.models import (
    OrganizationListResponse,
    OrganizationResponse,
)


# https://docs.pydantic.dev/latest/concepts/models/#rebuilding-model-schema
OrganizationResponse.model_rebuild()


def chromadb_upsert_organization(org: OrganizationResponse, collection):
    """Upsert organization into ChromaDB."""
    logger.debug(f"Upserting organization into ChromaDB: {org.id}")
    collection.upsert(
        documents=[str(org)],
        metadatas=[
            {
                "id": org.id,
                "type": org.type,
                "name": org.name,
                "short_name": org.shortName,
            }
        ],
        ids=[org.id],
    )


router = APIRouter()


@router.get(
    "/organizations/",
    tags=["oparl"],
    response_model=OrganizationResponse | OrganizationListResponse,
)
async def organizations(
    background_tasks: BackgroundTasks,
    organization_id: Optional[str] = Query(None, alias="id"),
    body_id: Optional[str] = Query(None, alias="body"),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_organizations_collection),
):
    """Get the organizations from the Stadt Bonn OParl API.

    see https://oparl.org/spezifikation/online-ansicht/#entity-organization
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/organizations"
    _response = None

    # if organization_id and body_id is provided, raise an error
    if organization_id is not None and body_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Please provide either id or body, not both.",
        )

    # if organization_id is None and body_id is None, return all organizations
    if organization_id is None and body_id is None:
        response = http_client.get(_url)
        if response.status_code == 200:
            _response = OrganizationListResponse(**response.json())
        else:
            logfire.error(
                "Failed to fetch organizations from OParl API",
                extra={"status_code": response.status_code, "url": _url},
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch organizations from OParl API",
            )

    # if organization_id is provided, return the organization with that id
    if organization_id and not body_id:
        response = http_client.get(
            _url + f"?typ=gr&id={organization_id}",
        )
        if response.status_code == 200:
            _json = response.json()
            if "membership" in _json:
                _json["membership_ref"] = [
                    membership for membership in _json["membership"]
                ]
            else:
                _json["membership_ref"] = None
            _json["membership"] = []

            _json["location_ref"] = _json.get("location", None).get("id", None)
            _json["location"] = None

            _json["meeting_ref"] = _json.get("meeting", None)

            _response = OrganizationResponse(**_json)

            result = OrganizationResponse(**_response.model_dump())
            background_tasks.add_task(chromadb_upsert_organization, result, collection)

            return result
        else:
            logfire.error(
                "Failed to fetch organizations from OParl API",
                extra={"status_code": response.status_code, "url": _url},
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch organizations from OParl API",
            )

    # if body_id is provided, return all organizations for that body
    if body_id:
        response = http_client.get(
            _url + f"?body={body_id}",
        )
        if response.status_code == 200:
            _response = OrganizationListResponse(**response.json())
        else:
            logfire.error(
                "Failed to fetch organizations from OParl API",
                extra={"status_code": response.status_code, "url": _url},
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch organizations from OParl API",
            )

    # if we have a response, return it
    if _response is not None and _response.model_rebuild():
        return _response
