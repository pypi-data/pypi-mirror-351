# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel

__all__ = ["IDGetByVenueResponse"]


class IDGetByVenueResponse(BaseModel):
    ids: Optional[List[str]] = None
    """List of production IDs"""
