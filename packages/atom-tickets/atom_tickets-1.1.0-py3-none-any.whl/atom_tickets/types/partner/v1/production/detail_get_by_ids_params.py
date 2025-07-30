# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["DetailGetByIDsParams"]


class DetailGetByIDsParams(TypedDict, total=False):
    ids: Required[List[str]]
    """List of production IDs to retrieve"""

    marketplace_id: Annotated[Optional[str], PropertyInfo(alias="marketplaceId")]
    """Marketplace identifier (US by default)"""

    page: Optional[int]
    """Page number for results"""

    page_size: Annotated[Optional[int], PropertyInfo(alias="pageSize")]
    """Number of results per page"""
