# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .details import (
    DetailsResource,
    AsyncDetailsResource,
    DetailsResourceWithRawResponse,
    AsyncDetailsResourceWithRawResponse,
    DetailsResourceWithStreamingResponse,
    AsyncDetailsResourceWithStreamingResponse,
)
from .showtimes import (
    ShowtimesResource,
    AsyncShowtimesResource,
    ShowtimesResourceWithRawResponse,
    AsyncShowtimesResourceWithRawResponse,
    ShowtimesResourceWithStreamingResponse,
    AsyncShowtimesResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from .by_vendor_venue_id.by_vendor_venue_id import (
    ByVendorVenueIDResource,
    AsyncByVendorVenueIDResource,
    ByVendorVenueIDResourceWithRawResponse,
    AsyncByVendorVenueIDResourceWithRawResponse,
    ByVendorVenueIDResourceWithStreamingResponse,
    AsyncByVendorVenueIDResourceWithStreamingResponse,
)

__all__ = ["VenueResource", "AsyncVenueResource"]


class VenueResource(SyncAPIResource):
    @cached_property
    def details(self) -> DetailsResource:
        return DetailsResource(self._client)

    @cached_property
    def by_vendor_venue_id(self) -> ByVendorVenueIDResource:
        return ByVendorVenueIDResource(self._client)

    @cached_property
    def showtimes(self) -> ShowtimesResource:
        return ShowtimesResource(self._client)

    @cached_property
    def with_raw_response(self) -> VenueResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return VenueResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VenueResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return VenueResourceWithStreamingResponse(self)


class AsyncVenueResource(AsyncAPIResource):
    @cached_property
    def details(self) -> AsyncDetailsResource:
        return AsyncDetailsResource(self._client)

    @cached_property
    def by_vendor_venue_id(self) -> AsyncByVendorVenueIDResource:
        return AsyncByVendorVenueIDResource(self._client)

    @cached_property
    def showtimes(self) -> AsyncShowtimesResource:
        return AsyncShowtimesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncVenueResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncVenueResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVenueResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncVenueResourceWithStreamingResponse(self)


class VenueResourceWithRawResponse:
    def __init__(self, venue: VenueResource) -> None:
        self._venue = venue

    @cached_property
    def details(self) -> DetailsResourceWithRawResponse:
        return DetailsResourceWithRawResponse(self._venue.details)

    @cached_property
    def by_vendor_venue_id(self) -> ByVendorVenueIDResourceWithRawResponse:
        return ByVendorVenueIDResourceWithRawResponse(self._venue.by_vendor_venue_id)

    @cached_property
    def showtimes(self) -> ShowtimesResourceWithRawResponse:
        return ShowtimesResourceWithRawResponse(self._venue.showtimes)


class AsyncVenueResourceWithRawResponse:
    def __init__(self, venue: AsyncVenueResource) -> None:
        self._venue = venue

    @cached_property
    def details(self) -> AsyncDetailsResourceWithRawResponse:
        return AsyncDetailsResourceWithRawResponse(self._venue.details)

    @cached_property
    def by_vendor_venue_id(self) -> AsyncByVendorVenueIDResourceWithRawResponse:
        return AsyncByVendorVenueIDResourceWithRawResponse(self._venue.by_vendor_venue_id)

    @cached_property
    def showtimes(self) -> AsyncShowtimesResourceWithRawResponse:
        return AsyncShowtimesResourceWithRawResponse(self._venue.showtimes)


class VenueResourceWithStreamingResponse:
    def __init__(self, venue: VenueResource) -> None:
        self._venue = venue

    @cached_property
    def details(self) -> DetailsResourceWithStreamingResponse:
        return DetailsResourceWithStreamingResponse(self._venue.details)

    @cached_property
    def by_vendor_venue_id(self) -> ByVendorVenueIDResourceWithStreamingResponse:
        return ByVendorVenueIDResourceWithStreamingResponse(self._venue.by_vendor_venue_id)

    @cached_property
    def showtimes(self) -> ShowtimesResourceWithStreamingResponse:
        return ShowtimesResourceWithStreamingResponse(self._venue.showtimes)


class AsyncVenueResourceWithStreamingResponse:
    def __init__(self, venue: AsyncVenueResource) -> None:
        self._venue = venue

    @cached_property
    def details(self) -> AsyncDetailsResourceWithStreamingResponse:
        return AsyncDetailsResourceWithStreamingResponse(self._venue.details)

    @cached_property
    def by_vendor_venue_id(self) -> AsyncByVendorVenueIDResourceWithStreamingResponse:
        return AsyncByVendorVenueIDResourceWithStreamingResponse(self._venue.by_vendor_venue_id)

    @cached_property
    def showtimes(self) -> AsyncShowtimesResourceWithStreamingResponse:
        return AsyncShowtimesResourceWithStreamingResponse(self._venue.showtimes)
