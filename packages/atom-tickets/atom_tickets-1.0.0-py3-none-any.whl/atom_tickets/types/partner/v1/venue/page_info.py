# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["PageInfo"]


class PageInfo(BaseModel):
    page: Optional[int] = None
    """Current page number"""

    page_size: Optional[int] = FieldInfo(alias="pageSize", default=None)
    """Number of items per page"""

    total_pages: Optional[int] = FieldInfo(alias="totalPages", default=None)
    """Total number of pages available"""
