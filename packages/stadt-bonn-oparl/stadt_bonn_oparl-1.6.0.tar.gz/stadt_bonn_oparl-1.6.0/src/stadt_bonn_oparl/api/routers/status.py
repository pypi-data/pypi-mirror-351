from fastapi import APIRouter, Depends
from pydantic import BaseModel

from stadt_bonn_oparl.api.dependencies import (
    chromadb_memberships_collection,
    chromadb_organizations_collection,
    chromadb_persons_collection,
)


class StatusResponse(BaseModel):
    status: str
    message: str
    document_count: int = 0


router = APIRouter()


@router.get("/status", tags=["service"], response_model=StatusResponse)
async def status(
    peeps=Depends(chromadb_persons_collection),
    orgs=Depends(chromadb_organizations_collection),
    members=Depends(chromadb_memberships_collection),
):
    """Get the status of the service."""
    try:
        return StatusResponse(
            status="ok",
            message="Service is running",
            document_count=peeps.count() + orgs.count() + members.count(),
        )
    except Exception as e:
        return StatusResponse(status="error", message=str(e))


@router.get("/status/persons", tags=["service"])
async def status_persons(
    peeps=Depends(chromadb_persons_collection),
):
    """Health check for persons collection."""
    try:
        return StatusResponse(
            status="ok",
            message="Persons collection is healthy",
            document_count=peeps.count(),
        )
    except Exception as e:
        return StatusResponse(status="error", message=str(e))


@router.get("/status/organizations", tags=["service"])
async def status_organizations(
    orgs=Depends(chromadb_organizations_collection),
):
    """Health check for organizations collection."""
    try:
        return StatusResponse(
            status="ok",
            message="Organizations collection is healthy",
            document_count=orgs.count(),
        )
    except Exception as e:
        return StatusResponse(status="error", message=str(e))
