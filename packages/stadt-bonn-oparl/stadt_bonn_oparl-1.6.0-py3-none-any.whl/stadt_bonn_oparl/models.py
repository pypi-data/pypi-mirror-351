import datetime
from typing import List, Optional

from pydantic import BaseModel


class OParlPerson(BaseModel):
    id: str
    name: str
    familyName: Optional[str] = None
    givenName: Optional[str] = None
    formOfAdress: Optional[str] = None
    affix: Optional[str] = None
    gender: Optional[str] = None
    location: Optional["OParlLocation"] = (
        None  # see that quotes? https://docs.pydantic.dev/latest/concepts/forward_annotations/
    )
    status: Optional[List[str]] = None
    membership: Optional[List["OParlMembership"]] = None
    web: Optional[str] = None


class OParlLocation(BaseModel):
    id: str
    description: str
    streetAddress: str
    postalCode: str
    locality: str


class OParlOrganization(BaseModel):
    id: str
    name: str
    shortName: str
    organizationType: str
    classification: str
    web: str
    location: Optional[OParlLocation] = None
    meeting: Optional[str] = (
        None  # this is a URL to query for the meetings references by this organization
    )
    membership: Optional[List["OParlMembership"]] = None
    startDate: Optional[datetime.date] = None
    endDate: Optional[datetime.date] = None


class OParlMeeting(BaseModel):
    id: str
    name: str
    description: str
    startDate: datetime.date
    endDate: datetime.date
    location: OParlLocation


class OParlMembership(BaseModel):
    id: str
    person: Optional[OParlPerson] = None
    organization: Optional[OParlOrganization] = None
    role: str
    votingRight: bool
    startDate: datetime.date
    endDate: Optional[datetime.date] = None
