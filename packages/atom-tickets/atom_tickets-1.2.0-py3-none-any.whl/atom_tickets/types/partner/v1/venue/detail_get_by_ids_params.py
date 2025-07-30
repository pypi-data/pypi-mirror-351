# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["DetailGetByIDsParams", "Location"]


class DetailGetByIDsParams(TypedDict, total=False):
    ids: Required[List[str]]
    """List of venue IDs to retrieve"""

    location: Optional[Location]
    """Location to calculate distance from"""

    page: Optional[int]
    """Page number for results"""

    page_size: Annotated[Optional[int], PropertyInfo(alias="pageSize")]
    """Number of results per page"""


class Location(TypedDict, total=False):
    lat: float
    """Latitude coordinate"""

    lon: float
    """Longitude coordinate"""
