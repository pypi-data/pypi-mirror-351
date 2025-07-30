# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = [
    "DetailGetForMultipleVenuesResponse",
    "AttributeMap",
    "ProductionDetailsMap",
    "ProductionDetailsMapContributors",
    "ProductionDetailsMapContributorsCast",
    "ProductionDetailsMapContributorsCrew",
    "ProductionDetailsMapProductionMedia",
    "ProductionDetailsMapProductionMediaImageData",
    "ProductionDetailsMapProductionMediaTrailerData",
    "VenueShowtimeDetailsMap",
    "VenueShowtimeDetailsMapPreOrderDetail",
    "VenueShowtimeDetailsMapShowtimeDetail",
    "VenueShowtimeDetailsMapShowtimeDetailOfferData",
    "VenueShowtimeDetailsMapShowtimeDetailOfferDataOffer",
    "VenueShowtimeDetailsMapShowtimeDetailOfferDataOfferPrice",
]


class AttributeMap(BaseModel):
    id: Optional[str] = None
    """Attribute identifier"""

    description: Optional[str] = None
    """Attribute description"""

    friendly_name: Optional[str] = FieldInfo(alias="friendlyName", default=None)
    """User-friendly attribute name"""

    icon_url: Optional[str] = FieldInfo(alias="iconUrl", default=None)
    """URL to attribute icon"""

    type: Optional[str] = None
    """Attribute type"""


class ProductionDetailsMapContributorsCast(BaseModel):
    character_name: Optional[str] = FieldInfo(alias="characterName", default=None)
    """Character name"""

    name: Optional[str] = None
    """Actor name"""


class ProductionDetailsMapContributorsCrew(BaseModel):
    name: Optional[str] = None
    """Crew member name"""

    role: Optional[str] = None
    """Crew member role"""


class ProductionDetailsMapContributors(BaseModel):
    cast: Optional[List[ProductionDetailsMapContributorsCast]] = None
    """List of cast members"""

    crew: Optional[List[ProductionDetailsMapContributorsCrew]] = None
    """List of crew members"""


class ProductionDetailsMapProductionMediaImageData(BaseModel):
    cover_image_url: Optional[str] = FieldInfo(alias="coverImageUrl", default=None)
    """URL to cover image"""

    promo_image_urls: Optional[List[str]] = FieldInfo(alias="promoImageUrls", default=None)
    """URLs to promotional images"""


class ProductionDetailsMapProductionMediaTrailerData(BaseModel):
    trailer_urls: Optional[List[str]] = FieldInfo(alias="trailerUrls", default=None)
    """URLs to trailer videos"""


class ProductionDetailsMapProductionMedia(BaseModel):
    image_data: Optional[ProductionDetailsMapProductionMediaImageData] = FieldInfo(alias="imageData", default=None)

    trailer_data: Optional[ProductionDetailsMapProductionMediaTrailerData] = FieldInfo(
        alias="trailerData", default=None
    )


class ProductionDetailsMap(BaseModel):
    id: Optional[str] = None
    """Production identifier"""

    advisory_rating: Optional[str] = FieldInfo(alias="advisoryRating", default=None)
    """Advisory rating (PG, PG-13, R, etc.)"""

    atom_production_id: Optional[str] = FieldInfo(alias="atomProductionId", default=None)
    """Atom Tickets internal production ID"""

    atom_user_score: Optional[float] = FieldInfo(alias="atomUserScore", default=None)
    """User score on Atom Tickets"""

    contributors: Optional[ProductionDetailsMapContributors] = None

    distributor: Optional[str] = None
    """Distributor name"""

    genres: Optional[List[str]] = None
    """List of genres"""

    imdb_id: Optional[str] = FieldInfo(alias="imdbId", default=None)
    """IMDB identifier"""

    name: Optional[str] = None
    """Production name"""

    production_media: Optional[ProductionDetailsMapProductionMedia] = FieldInfo(alias="productionMedia", default=None)

    production_url: Optional[str] = FieldInfo(alias="productionUrl", default=None)
    """URL to production page on Atom Tickets"""

    release_date: Optional[str] = FieldInfo(alias="releaseDate", default=None)
    """Release date in format YYYY-MM-DD"""

    runtime_minutes: Optional[int] = FieldInfo(alias="runtimeMinutes", default=None)
    """Runtime in minutes"""

    synopsis: Optional[str] = None
    """Production synopsis"""


class VenueShowtimeDetailsMapPreOrderDetail(BaseModel):
    production_id: Optional[str] = FieldInfo(alias="productionId", default=None)
    """Production identifier"""

    showtime_days: Optional[List[str]] = FieldInfo(alias="showtimeDays", default=None)
    """List of days with showtimes available for pre-order"""

    venue_id: Optional[str] = FieldInfo(alias="venueId", default=None)
    """Venue identifier"""


class VenueShowtimeDetailsMapShowtimeDetailOfferDataOfferPrice(BaseModel):
    currency_code: Optional[str] = FieldInfo(alias="currencyCode", default=None)
    """Currency code (e.g., USD)"""

    value: Optional[float] = None
    """Price value"""


class VenueShowtimeDetailsMapShowtimeDetailOfferDataOffer(BaseModel):
    label: Optional[str] = None
    """Offer label (e.g., Matinee, Senior)"""

    price: Optional[VenueShowtimeDetailsMapShowtimeDetailOfferDataOfferPrice] = None


class VenueShowtimeDetailsMapShowtimeDetailOfferData(BaseModel):
    offers: Optional[List[VenueShowtimeDetailsMapShowtimeDetailOfferDataOffer]] = None
    """List of price offers"""


class VenueShowtimeDetailsMapShowtimeDetail(BaseModel):
    attributes: Optional[List[str]] = None
    """List of attribute keys for the attributeMap"""

    available_inventory: Optional[int] = FieldInfo(alias="availableInventory", default=None)
    """Number of available seats"""

    checkout_url: Optional[str] = FieldInfo(alias="checkoutUrl", default=None)
    """URL to checkout page on Atom Tickets"""

    local_showtime_start: Optional[datetime] = FieldInfo(alias="localShowtimeStart", default=None)
    """Local showtime start in ISO8601 format without milliseconds"""

    offer_data: Optional[VenueShowtimeDetailsMapShowtimeDetailOfferData] = FieldInfo(alias="offerData", default=None)

    production_id: Optional[str] = FieldInfo(alias="productionId", default=None)
    """Production identifier"""

    showtime_id: Optional[str] = FieldInfo(alias="showtimeId", default=None)
    """Showtime identifier"""

    tags: Optional[List[str]] = None
    """Tags for special event showtimes"""

    utc_showtime_start: Optional[datetime] = FieldInfo(alias="utcShowtimeStart", default=None)
    """UTC showtime start in ISO8601 format without milliseconds"""

    venue_id: Optional[str] = FieldInfo(alias="venueId", default=None)
    """Venue identifier"""


class VenueShowtimeDetailsMap(BaseModel):
    pre_order_details: Optional[List[VenueShowtimeDetailsMapPreOrderDetail]] = FieldInfo(
        alias="preOrderDetails", default=None
    )

    showtime_details: Optional[List[VenueShowtimeDetailsMapShowtimeDetail]] = FieldInfo(
        alias="showtimeDetails", default=None
    )


class DetailGetForMultipleVenuesResponse(BaseModel):
    attribute_map: Optional[Dict[str, AttributeMap]] = FieldInfo(alias="attributeMap", default=None)
    """Map of attribute keys to attribute details"""

    production_details_map: Optional[Dict[str, ProductionDetailsMap]] = FieldInfo(
        alias="productionDetailsMap", default=None
    )
    """Map of production IDs to production details"""

    venue_showtime_details_map: Optional[Dict[str, VenueShowtimeDetailsMap]] = FieldInfo(
        alias="venueShowtimeDetailsMap", default=None
    )
    """Map of venue IDs to venue showtime details"""
