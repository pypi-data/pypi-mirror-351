# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel
from ..venue.page_info import PageInfo

__all__ = [
    "ProductionDetails",
    "ProductionDetail",
    "ProductionDetailContributors",
    "ProductionDetailContributorsCast",
    "ProductionDetailContributorsCrew",
    "ProductionDetailProductionMedia",
    "ProductionDetailProductionMediaImageData",
    "ProductionDetailProductionMediaTrailerData",
]


class ProductionDetailContributorsCast(BaseModel):
    character_name: Optional[str] = FieldInfo(alias="characterName", default=None)
    """Character name"""

    name: Optional[str] = None
    """Actor name"""


class ProductionDetailContributorsCrew(BaseModel):
    name: Optional[str] = None
    """Crew member name"""

    role: Optional[str] = None
    """Crew member role"""


class ProductionDetailContributors(BaseModel):
    cast: Optional[List[ProductionDetailContributorsCast]] = None
    """List of cast members"""

    crew: Optional[List[ProductionDetailContributorsCrew]] = None
    """List of crew members"""


class ProductionDetailProductionMediaImageData(BaseModel):
    cover_image_url: Optional[str] = FieldInfo(alias="coverImageUrl", default=None)
    """URL to cover image"""

    promo_image_urls: Optional[List[str]] = FieldInfo(alias="promoImageUrls", default=None)
    """URLs to promotional images"""


class ProductionDetailProductionMediaTrailerData(BaseModel):
    trailer_urls: Optional[List[str]] = FieldInfo(alias="trailerUrls", default=None)
    """URLs to trailer videos"""


class ProductionDetailProductionMedia(BaseModel):
    image_data: Optional[ProductionDetailProductionMediaImageData] = FieldInfo(alias="imageData", default=None)

    trailer_data: Optional[ProductionDetailProductionMediaTrailerData] = FieldInfo(alias="trailerData", default=None)


class ProductionDetail(BaseModel):
    id: Optional[str] = None
    """Production identifier"""

    advisory_rating: Optional[str] = FieldInfo(alias="advisoryRating", default=None)
    """Advisory rating (PG, PG-13, R, etc.)"""

    atom_production_id: Optional[str] = FieldInfo(alias="atomProductionId", default=None)
    """Atom Tickets internal production ID"""

    atom_user_score: Optional[float] = FieldInfo(alias="atomUserScore", default=None)
    """User score on Atom Tickets"""

    contributors: Optional[ProductionDetailContributors] = None

    distributor: Optional[str] = None
    """Distributor name"""

    genres: Optional[List[str]] = None
    """List of genres"""

    imdb_id: Optional[str] = FieldInfo(alias="imdbId", default=None)
    """IMDB identifier"""

    name: Optional[str] = None
    """Production name"""

    production_media: Optional[ProductionDetailProductionMedia] = FieldInfo(alias="productionMedia", default=None)

    production_url: Optional[str] = FieldInfo(alias="productionUrl", default=None)
    """URL to production page on Atom Tickets"""

    release_date: Optional[str] = FieldInfo(alias="releaseDate", default=None)
    """Release date in format YYYY-MM-DD"""

    runtime_minutes: Optional[int] = FieldInfo(alias="runtimeMinutes", default=None)
    """Runtime in minutes"""

    synopsis: Optional[str] = None
    """Production synopsis"""


class ProductionDetails(BaseModel):
    page_info: Optional[PageInfo] = FieldInfo(alias="pageInfo", default=None)

    production_details: Optional[List[ProductionDetail]] = FieldInfo(alias="productionDetails", default=None)
