# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["DetailGetForMultipleVenuesParams", "ISODateBounds", "LocalDateBounds"]


class DetailGetForMultipleVenuesParams(TypedDict, total=False):
    venue_ids: Required[Annotated[List[str], PropertyInfo(alias="venueIds")]]
    """Set of venue IDs to retrieve showtimes for"""

    include_production_details: Annotated[Optional[bool], PropertyInfo(alias="includeProductionDetails")]
    """Whether to include production details in response"""

    iso_date_bounds: Annotated[Optional[ISODateBounds], PropertyInfo(alias="isoDateBounds")]
    """Date bounds in ISO format"""

    local_date_bounds: Annotated[Optional[LocalDateBounds], PropertyInfo(alias="localDateBounds")]
    """Date bounds in local format"""

    marketplace_id: Annotated[Optional[str], PropertyInfo(alias="marketplaceId")]
    """Marketplace identifier"""

    production_ids: Annotated[Optional[List[str]], PropertyInfo(alias="productionIds")]
    """Set of production IDs to filter showtimes by"""


class ISODateBounds(TypedDict, total=False):
    iso_end_date: Annotated[Union[str, datetime], PropertyInfo(alias="isoEndDate", format="iso8601")]
    """ISO8601 formatted end date without milliseconds"""

    iso_start_date: Annotated[Union[str, datetime], PropertyInfo(alias="isoStartDate", format="iso8601")]
    """ISO8601 formatted start date without milliseconds"""


class LocalDateBounds(TypedDict, total=False):
    local_end_date: Annotated[str, PropertyInfo(alias="localEndDate")]
    """Local end date in format YYYY-MM-DDTHH:MM:SS (no timezone)"""

    local_start_date: Annotated[str, PropertyInfo(alias="localStartDate")]
    """Local start date in format YYYY-MM-DDTHH:MM:SS (no timezone)"""
