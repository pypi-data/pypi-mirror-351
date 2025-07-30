# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ...._compat import cached_property
from .venue.venue import (
    VenueResource,
    AsyncVenueResource,
    VenueResourceWithRawResponse,
    AsyncVenueResourceWithRawResponse,
    VenueResourceWithStreamingResponse,
    AsyncVenueResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from .showtime.showtime import (
    ShowtimeResource,
    AsyncShowtimeResource,
    ShowtimeResourceWithRawResponse,
    AsyncShowtimeResourceWithRawResponse,
    ShowtimeResourceWithStreamingResponse,
    AsyncShowtimeResourceWithStreamingResponse,
)
from .production.production import (
    ProductionResource,
    AsyncProductionResource,
    ProductionResourceWithRawResponse,
    AsyncProductionResourceWithRawResponse,
    ProductionResourceWithStreamingResponse,
    AsyncProductionResourceWithStreamingResponse,
)

__all__ = ["V1Resource", "AsyncV1Resource"]


class V1Resource(SyncAPIResource):
    @cached_property
    def showtime(self) -> ShowtimeResource:
        return ShowtimeResource(self._client)

    @cached_property
    def venue(self) -> VenueResource:
        return VenueResource(self._client)

    @cached_property
    def production(self) -> ProductionResource:
        return ProductionResource(self._client)

    @cached_property
    def with_raw_response(self) -> V1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return V1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return V1ResourceWithStreamingResponse(self)


class AsyncV1Resource(AsyncAPIResource):
    @cached_property
    def showtime(self) -> AsyncShowtimeResource:
        return AsyncShowtimeResource(self._client)

    @cached_property
    def venue(self) -> AsyncVenueResource:
        return AsyncVenueResource(self._client)

    @cached_property
    def production(self) -> AsyncProductionResource:
        return AsyncProductionResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncV1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncV1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncV1ResourceWithStreamingResponse(self)


class V1ResourceWithRawResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

    @cached_property
    def showtime(self) -> ShowtimeResourceWithRawResponse:
        return ShowtimeResourceWithRawResponse(self._v1.showtime)

    @cached_property
    def venue(self) -> VenueResourceWithRawResponse:
        return VenueResourceWithRawResponse(self._v1.venue)

    @cached_property
    def production(self) -> ProductionResourceWithRawResponse:
        return ProductionResourceWithRawResponse(self._v1.production)


class AsyncV1ResourceWithRawResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

    @cached_property
    def showtime(self) -> AsyncShowtimeResourceWithRawResponse:
        return AsyncShowtimeResourceWithRawResponse(self._v1.showtime)

    @cached_property
    def venue(self) -> AsyncVenueResourceWithRawResponse:
        return AsyncVenueResourceWithRawResponse(self._v1.venue)

    @cached_property
    def production(self) -> AsyncProductionResourceWithRawResponse:
        return AsyncProductionResourceWithRawResponse(self._v1.production)


class V1ResourceWithStreamingResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

    @cached_property
    def showtime(self) -> ShowtimeResourceWithStreamingResponse:
        return ShowtimeResourceWithStreamingResponse(self._v1.showtime)

    @cached_property
    def venue(self) -> VenueResourceWithStreamingResponse:
        return VenueResourceWithStreamingResponse(self._v1.venue)

    @cached_property
    def production(self) -> ProductionResourceWithStreamingResponse:
        return ProductionResourceWithStreamingResponse(self._v1.production)


class AsyncV1ResourceWithStreamingResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

    @cached_property
    def showtime(self) -> AsyncShowtimeResourceWithStreamingResponse:
        return AsyncShowtimeResourceWithStreamingResponse(self._v1.showtime)

    @cached_property
    def venue(self) -> AsyncVenueResourceWithStreamingResponse:
        return AsyncVenueResourceWithStreamingResponse(self._v1.venue)

    @cached_property
    def production(self) -> AsyncProductionResourceWithStreamingResponse:
        return AsyncProductionResourceWithStreamingResponse(self._v1.production)
