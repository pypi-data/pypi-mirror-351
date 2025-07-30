from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from stadt_bonn_oparl.api.dependencies import (
    http_client_factory,
)
from stadt_bonn_oparl.api.models import (
    MeetingListResponse,
    MeetingResponse,
)


def chromadb_upsert_meeting(data: MeetingResponse, collection):
    """Upsert meeting into ChromaDB."""
    collection.upsert(
        documents=[str(data)],
        metadatas=[
            {
                id: data.id,
                "name": data.name,
                "description": data.description,
                "startDate": data.startDate.isoformat() if data.startDate else None,
                "endDate": data.endDate.isoformat() if data.endDate else None,
                "location": str(data.location) if data.location else None,
            }
        ],
        ids=[data.id],
    )


router = APIRouter()


@router.get("/meetings", tags=["oparl"], response_model=MeetingResponse)
async def meetings(
    meeting_id: Optional[str] = Query(None, alias="id"),
    body_id: Optional[str] = Query(None, alias="body"),
    organization_id: Optional[str] = Query(None, alias="organization"),
    page: Optional[int] = Query(1, ge=1, le=1000),
    http_client: httpx.Client = Depends(http_client_factory),
) -> MeetingListResponse | MeetingResponse:
    """Get the meetings from the Stadt Bonn OParl API.

    see https://oparl.org/spezifikation/online-ansicht/#entity-meeting
    """
    # This endpoint is not implemented yet
    raise HTTPException(status_code=501, detail="Meetings endpoint not implemented yet")
