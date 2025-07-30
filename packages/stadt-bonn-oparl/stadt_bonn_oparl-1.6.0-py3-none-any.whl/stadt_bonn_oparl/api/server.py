from typing import Optional

import httpx
import logfire
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import ValidationError

import stadt_bonn_oparl
from stadt_bonn_oparl.api.dependencies import (
    chromadb_persons_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.models import (
    LocationResponse,
    SystemResponse,
)
from stadt_bonn_oparl.api.routers import (
    meetings,
    memberships,
    organizations,
    persons,
    status,
)
from stadt_bonn_oparl.logging import configure_logging

configure_logging(2)
logfire.configure(
    service_name="stadt-bonn-oparl-cache",
    service_version=stadt_bonn_oparl.__version__,
)


app = FastAPI(
    title="Stadt Bonn OParl (partial) caching read-only-API",
    description="A search and cache for the Stadt Bonn OParl API to speed up access and reduce load on the original API.",
    version=stadt_bonn_oparl.__version__,
    contact={
        "name": "Mach! Den! Staat!",
        "url": "https://machdenstaat.de",
    },
)

app.include_router(meetings.router)
app.include_router(memberships.router)
app.include_router(organizations.router)
app.include_router(persons.router)
app.include_router(status.router)

logfire.instrument_fastapi(app)
logfire.instrument_httpx()


@app.get("/version", tags=["service"])
async def version():
    """Get the version information for the Stadt Bonn OParl API Cache."""
    return {"version": stadt_bonn_oparl.__version__, "name": "stadt-bonn-oparl-cache"}


@app.get("/system", tags=["oparl"], response_model=SystemResponse)
async def system(
    http_client: httpx.Client = Depends(http_client_factory),
) -> SystemResponse:
    """Get the system information from the Stadt Bonn OParl API.

    see https://oparl.org/spezifikation/online-ansicht/#entity-system
    """
    # use httpx to talk to the Stadt Bonn OParl API
    # and return the system information

    response = http_client.get("https://www.bonn.sitzung-online.de/public/oparl/system")
    if response.status_code == 200:
        system = SystemResponse(**response.json())
        # let's fix the body attribute, it should point to a body object not an index
        # this is a workaround for the OParl API not following the spec correctly
        return system
    else:
        raise HTTPException(
            status_code=500, detail="Failed to fetch system information from OParl API"
        )


@app.get("/bodies/", tags=["oparl"])
async def bodies(
    body_id: Optional[str] = Query(None, alias="id"),
    http_client: httpx.Client = Depends(http_client_factory),
):
    """Get the bodies from the Stadt Bonn OParl API.

    see https://oparl.org/spezifikation/online-ansicht/#entity-body
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/bodies"

    if body_id is None:
        response = http_client.get(_url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch bodies from OParl API"}

    if body_id != "1":
        return {"error": "Invalid body ID. Only '1' is supported."}

    response = http_client.get(
        _url + f"?id={body_id}",
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch bodies from OParl API"}


@app.get("/locations", tags=["oparl"])
async def locations(
    location_id: Optional[str] = Query(None, alias="id"),
    http_client: httpx.Client = Depends(http_client_factory),
) -> LocationResponse:
    """Get the locations from the Stadt Bonn OParl API.

    see https://oparl.org/spezifikation/online-ansicht/#entity-location
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/locations"

    if location_id is None:
        raise HTTPException(status_code=400, detail="Location ID is required")

    _url += f"?id={location_id}"

    response = http_client.get(_url)
    if response.status_code == 200:
        try:
            return LocationResponse(**response.json())
        except ValidationError as e:
            logfire.error(
                f"Failed to parse location response: {e}",
                extra={"response": response.json()},
            )
            raise HTTPException(
                status_code=404, detail="Failed to find/fetch locations from OParl API"
            )
    else:
        raise HTTPException(
            status_code=500, detail="Failed to fetch locations from OParl API"
        )


@app.get("/search", tags=["oparl"])
async def search(
    query: str = Query(..., description="Search query for entities"),
    entity_type: Optional[str] = Query(
        None, description="Type of entity to search for (e.g., person, organization)"
    ),
    page: Optional[int] = Query(
        1, ge=1, le=1000, description="Page number for results"
    ),
    collection=Depends(chromadb_persons_collection),
):
    """Search for entities in the Stadt Bonn OParl API.

    **This endpoint is not implemented yet!**
    """
    search_results = collection.query(
        query_texts=[query],
        n_results=5,
    )
    return search_results
