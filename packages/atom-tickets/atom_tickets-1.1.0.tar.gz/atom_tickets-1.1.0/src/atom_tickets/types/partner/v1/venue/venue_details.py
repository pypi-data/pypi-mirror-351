# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .page_info import PageInfo
from ....._models import BaseModel

__all__ = ["VenueDetails", "VenueDetail", "VenueDetailVenue", "VenueDetailVenueAddress", "VenueDetailVenueProperties"]


class VenueDetailVenueAddress(BaseModel):
    city: Optional[str] = None
    """City name"""

    lat: Optional[float] = None
    """Latitude coordinate"""

    line: Optional[str] = None
    """Street address line"""

    lon: Optional[float] = None
    """Longitude coordinate"""

    postal: Optional[str] = None
    """Postal code"""

    state: Optional[str] = None
    """State abbreviation"""


class VenueDetailVenueProperties(BaseModel):
    supported: Optional[bool] = None
    """Whether venue is supported by Atom Tickets"""

    supports_concessions: Optional[bool] = FieldInfo(alias="supportsConcessions", default=None)
    """Whether venue supports concessions"""


class VenueDetailVenue(BaseModel):
    id: Optional[str] = None
    """Venue identifier"""

    address: Optional[VenueDetailVenueAddress] = None

    atom_venue_id: Optional[str] = FieldInfo(alias="atomVenueId", default=None)
    """Atom Tickets internal venue ID"""

    name: Optional[str] = None
    """Venue name"""

    properties: Optional[VenueDetailVenueProperties] = None

    venue_url: Optional[str] = FieldInfo(alias="venueUrl", default=None)
    """URL to venue page on Atom Tickets"""


class VenueDetail(BaseModel):
    km_distance: Optional[float] = FieldInfo(alias="kmDistance", default=None)
    """Distance from specified location in kilometers"""

    venue: Optional[VenueDetailVenue] = None


class VenueDetails(BaseModel):
    page_info: Optional[PageInfo] = FieldInfo(alias="pageInfo", default=None)

    venue_details: Optional[List[VenueDetail]] = FieldInfo(alias="venueDetails", default=None)
