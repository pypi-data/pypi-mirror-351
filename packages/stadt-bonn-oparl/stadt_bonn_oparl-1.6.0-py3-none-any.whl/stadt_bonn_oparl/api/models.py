import datetime
from typing import List, Optional

from pydantic import BaseModel
from regex import W

from stadt_bonn_oparl.models import (
    OParlLocation,
    OParlMeeting,
    OParlMembership,
    OParlOrganization,
    OParlPerson,
)


class OParlResponse(BaseModel):
    """Base model for OParl API responses."""

    id: str

    created: datetime.datetime
    modified: datetime.datetime
    deleted: bool = False


class SystemResponse(OParlResponse):
    """Model for the system response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/System"
    oparlVersion: str = "https://schema.oparl.org/1.1/"
    otherOparlVersions: Optional[list[str]] = None
    license: Optional[str]
    body: str
    name: str
    contactEmail: Optional[str] = None
    contactName: Optional[str] = None
    website: Optional[str] = None
    vendor: str = "Mach! Den! Staat!"
    product: str = "Stadt Bonn OParl API Cache"


class PersonResponse(OParlResponse, OParlPerson):
    """Model for the person response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Person"

    membership_ref: Optional[List[str]] = None
    location_ref: Optional[str] = None


class PersonListResponse(BaseModel):
    """Model for a list of persons from the OParl API."""

    data: List[PersonResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class MembershipResponse(OParlResponse, OParlMembership):
    """Model for the membership response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Membership"

    person_ref: Optional[str] = None  # Internal use only, not part of the OParl schema

    organization_ref: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )


class MembershipListResponse(BaseModel):
    """Model for a list of memberships from the OParl API."""

    data: List[MembershipResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class LocationResponse(OParlResponse, OParlLocation):
    """Model for the location response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Location"


class LocationListResponse(BaseModel):
    """Model for a list of locations from the OParl API."""

    data: List[LocationResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class OrganizationResponse(OParlResponse, OParlOrganization):
    """Model for the organization response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Organization"

    membership_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    location_ref: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )
    meeting_ref: Optional[str] = None  # Internal use only, not part of the OParl schema


class OrganizationListResponse(BaseModel):
    """Model for a list of organizations from the OParl API."""

    data: List[OrganizationResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class MeetingResponse(OParlResponse, OParlMeeting):
    """Model for the meeting response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Meeting"


class MeetingListResponse(BaseModel):
    """Model for a list of meetings from the OParl API."""

    data: List[MeetingResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None
