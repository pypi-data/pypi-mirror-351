# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["DetailGetByLocationParams"]


class DetailGetByLocationParams(TypedDict, total=False):
    lat: Required[float]
    """Latitude coordinate"""

    lon: Required[float]
    """Longitude coordinate"""

    page: int
    """Page number for results"""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Number of results per page (max 100)"""

    radius: float
    """Search radius in kilometers (max 80km)"""
