# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = [
    "ShowtimeDetails",
    "AttributeMap",
    "PreOrderDetail",
    "ShowtimeDetail",
    "ShowtimeDetailOfferData",
    "ShowtimeDetailOfferDataOffer",
    "ShowtimeDetailOfferDataOfferPrice",
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


class PreOrderDetail(BaseModel):
    production_id: Optional[str] = FieldInfo(alias="productionId", default=None)
    """Production identifier"""

    showtime_days: Optional[List[str]] = FieldInfo(alias="showtimeDays", default=None)
    """List of days with showtimes available for pre-order"""

    venue_id: Optional[str] = FieldInfo(alias="venueId", default=None)
    """Venue identifier"""


class ShowtimeDetailOfferDataOfferPrice(BaseModel):
    currency_code: Optional[str] = FieldInfo(alias="currencyCode", default=None)
    """Currency code (e.g., USD)"""

    value: Optional[float] = None
    """Price value"""


class ShowtimeDetailOfferDataOffer(BaseModel):
    label: Optional[str] = None
    """Offer label (e.g., Matinee, Senior)"""

    price: Optional[ShowtimeDetailOfferDataOfferPrice] = None


class ShowtimeDetailOfferData(BaseModel):
    offers: Optional[List[ShowtimeDetailOfferDataOffer]] = None
    """List of price offers"""


class ShowtimeDetail(BaseModel):
    attributes: Optional[List[str]] = None
    """List of attribute keys for the attributeMap"""

    available_inventory: Optional[int] = FieldInfo(alias="availableInventory", default=None)
    """Number of available seats"""

    checkout_url: Optional[str] = FieldInfo(alias="checkoutUrl", default=None)
    """URL to checkout page on Atom Tickets"""

    local_showtime_start: Optional[datetime] = FieldInfo(alias="localShowtimeStart", default=None)
    """Local showtime start in ISO8601 format without milliseconds"""

    offer_data: Optional[ShowtimeDetailOfferData] = FieldInfo(alias="offerData", default=None)

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


class ShowtimeDetails(BaseModel):
    attribute_map: Optional[Dict[str, AttributeMap]] = FieldInfo(alias="attributeMap", default=None)
    """Map of attribute keys to attribute details"""

    pre_order_details: Optional[List[PreOrderDetail]] = FieldInfo(alias="preOrderDetails", default=None)

    showtime_details: Optional[List[ShowtimeDetail]] = FieldInfo(alias="showtimeDetails", default=None)
