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
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["ShowtimeResource", "AsyncShowtimeResource"]


class ShowtimeResource(SyncAPIResource):
    @cached_property
    def details(self) -> DetailsResource:
        return DetailsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ShowtimeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return ShowtimeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ShowtimeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return ShowtimeResourceWithStreamingResponse(self)


class AsyncShowtimeResource(AsyncAPIResource):
    @cached_property
    def details(self) -> AsyncDetailsResource:
        return AsyncDetailsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncShowtimeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncShowtimeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncShowtimeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncShowtimeResourceWithStreamingResponse(self)


class ShowtimeResourceWithRawResponse:
    def __init__(self, showtime: ShowtimeResource) -> None:
        self._showtime = showtime

    @cached_property
    def details(self) -> DetailsResourceWithRawResponse:
        return DetailsResourceWithRawResponse(self._showtime.details)


class AsyncShowtimeResourceWithRawResponse:
    def __init__(self, showtime: AsyncShowtimeResource) -> None:
        self._showtime = showtime

    @cached_property
    def details(self) -> AsyncDetailsResourceWithRawResponse:
        return AsyncDetailsResourceWithRawResponse(self._showtime.details)


class ShowtimeResourceWithStreamingResponse:
    def __init__(self, showtime: ShowtimeResource) -> None:
        self._showtime = showtime

    @cached_property
    def details(self) -> DetailsResourceWithStreamingResponse:
        return DetailsResourceWithStreamingResponse(self._showtime.details)


class AsyncShowtimeResourceWithStreamingResponse:
    def __init__(self, showtime: AsyncShowtimeResource) -> None:
        self._showtime = showtime

    @cached_property
    def details(self) -> AsyncDetailsResourceWithStreamingResponse:
        return AsyncDetailsResourceWithStreamingResponse(self._showtime.details)
