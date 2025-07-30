# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["DetailGetByVenueParams"]


class DetailGetByVenueParams(TypedDict, total=False):
    iso_end_date: Required[Annotated[Union[str, datetime], PropertyInfo(alias="isoEndDate", format="iso8601")]]
    """ISO8601 formatted end date without milliseconds"""

    iso_start_date: Required[Annotated[Union[str, datetime], PropertyInfo(alias="isoStartDate", format="iso8601")]]
    """ISO8601 formatted start date without milliseconds"""
