from fastapi import HTTPException
import httpx

from stadt_bonn_oparl.api.models import (
    MembershipResponse,
    PersonResponse,
)


async def _get_memberships(
    http_client: httpx.Client, membership_id: str
) -> MembershipResponse:
    """Helper function to get a membership by ID from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/memberships"

    response = http_client.get(_url + f"?id={membership_id}")
    if response.status_code == 200:
        _json = response.json()

        _json["person_ref"] = _json.get("person", None)
        _json["person"] = None
        _json["organization_ref"] = _json.get("organization", None)
        _json["organization"] = None

        return MembershipResponse(**_json)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch membership {membership_id} information from OParl API",
        )


async def _get_person(http_client: httpx.Client, person_id: str) -> PersonResponse:
    """Helper function to get a person by ID from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/persons"

    response = http_client.get(_url + f"?id={person_id}")
    if response.status_code == 200:
        _json = response.json()

        # _json['membership_ref'] shall be all the IDs from the memberships
        if "membership" in _json:
            _json["membership_ref"] = [
                membership["id"] for membership in _json["membership"]
            ]
        else:
            _json["membership_ref"] = None
        _json["membership"] = None
        _json["location_ref"] = _json["location"] if "location" in _json else None
        _json["location"] = None

        return PersonResponse(**_json)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch person {person_id} information from OParl API",
        )
