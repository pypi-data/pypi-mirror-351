from typing import Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger

from stadt_bonn_oparl.api.dependencies import (
    chromadb_memberships_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.models import (
    MembershipListResponse,
    MembershipResponse,
)


def chromadb_upsert_membership(membership: MembershipResponse, collection):
    """Upsert membership into ChromaDB."""
    logger.debug(f"Upserting membership into ChromaDB: {membership.id}")
    collection.upsert(
        documents=[str(membership)],
        metadatas=[
            {
                "id": membership.id,
                "type": membership.type,
            }
        ],
        ids=[membership.id],
    )


router = APIRouter()


@router.get(
    "/memberships",
    tags=["oparl"],
    response_model=MembershipResponse | MembershipListResponse,
)
async def memberships(
    background_tasks: BackgroundTasks,
    membership_id: Optional[str] = Query(None, alias="id"),
    person_id: Optional[str] = Query(None, alias="person"),
    body_id: Optional[str] = Query(None, alias="body"),
    page: Optional[int] = Query(1, ge=1, le=1000),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_memberships_collection),
):
    """Get the memberships from the Stadt Bonn OParl API.

    see https://oparl.org/spezifikation/online-ansicht/#entity-membership
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/memberships"
    _response = None

    if membership_id and (person_id or body_id):
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch membership information from OParl API: too many parameters provided.",
        )

    if membership_id is None and person_id is None and body_id is None:
        response = http_client.get(_url)
        if response.status_code == 200:
            return MembershipListResponse(**response.json())
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch membership information from OParl API",
            )

    if membership_id and not person_id and not body_id:
        response = http_client.get(_url + f"?id={membership_id}")
        if response.status_code == 200:
            _json = response.json()

            _json["person_ref"] = _json.get("person", None)
            _json["person"] = None

            _json["organization_ref"] = _json.get("organization", None)
            _json["organization"] = None

            result = MembershipResponse(**_json)
            background_tasks.add_task(chromadb_upsert_membership, result, collection)

            return result
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch membership information from OParl API",
            )

    if person_id and not body_id:
        response = http_client.get(_url + f"?person={person_id}")
        if response.status_code == 200:
            return MembershipListResponse(**response.json())
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch membership information from OParl API",
            )

    if body_id:
        response = http_client.get(_url + f"?body={body_id}")
        if response.status_code == 200:
            return MembershipListResponse(**response.json())
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch membership information from OParl API",
            )
