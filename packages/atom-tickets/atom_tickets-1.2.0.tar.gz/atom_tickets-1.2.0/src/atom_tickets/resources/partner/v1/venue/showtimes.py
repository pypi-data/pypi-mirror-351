# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.partner.v1.showtime.showtime_details import ShowtimeDetails

__all__ = ["ShowtimesResource", "AsyncShowtimesResource"]


class ShowtimesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ShowtimesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return ShowtimesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ShowtimesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return ShowtimesResourceWithStreamingResponse(self)

    def get_by_vendor_showtime_id(
        self,
        vendor_showtime_id: str,
        *,
        venue_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ShowtimeDetails:
        """
        Returns showtime details for a vendor-specific showtime ID at a specified venue

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not venue_id:
            raise ValueError(f"Expected a non-empty value for `venue_id` but received {venue_id!r}")
        if not vendor_showtime_id:
            raise ValueError(f"Expected a non-empty value for `vendor_showtime_id` but received {vendor_showtime_id!r}")
        return self._get(
            f"/partner/v1/venues/{venue_id}/showtimes/byVendorShowtimeId/{vendor_showtime_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShowtimeDetails,
        )


class AsyncShowtimesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncShowtimesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncShowtimesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncShowtimesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncShowtimesResourceWithStreamingResponse(self)

    async def get_by_vendor_showtime_id(
        self,
        vendor_showtime_id: str,
        *,
        venue_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ShowtimeDetails:
        """
        Returns showtime details for a vendor-specific showtime ID at a specified venue

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not venue_id:
            raise ValueError(f"Expected a non-empty value for `venue_id` but received {venue_id!r}")
        if not vendor_showtime_id:
            raise ValueError(f"Expected a non-empty value for `vendor_showtime_id` but received {vendor_showtime_id!r}")
        return await self._get(
            f"/partner/v1/venues/{venue_id}/showtimes/byVendorShowtimeId/{vendor_showtime_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShowtimeDetails,
        )


class ShowtimesResourceWithRawResponse:
    def __init__(self, showtimes: ShowtimesResource) -> None:
        self._showtimes = showtimes

        self.get_by_vendor_showtime_id = to_raw_response_wrapper(
            showtimes.get_by_vendor_showtime_id,
        )


class AsyncShowtimesResourceWithRawResponse:
    def __init__(self, showtimes: AsyncShowtimesResource) -> None:
        self._showtimes = showtimes

        self.get_by_vendor_showtime_id = async_to_raw_response_wrapper(
            showtimes.get_by_vendor_showtime_id,
        )


class ShowtimesResourceWithStreamingResponse:
    def __init__(self, showtimes: ShowtimesResource) -> None:
        self._showtimes = showtimes

        self.get_by_vendor_showtime_id = to_streamed_response_wrapper(
            showtimes.get_by_vendor_showtime_id,
        )


class AsyncShowtimesResourceWithStreamingResponse:
    def __init__(self, showtimes: AsyncShowtimesResource) -> None:
        self._showtimes = showtimes

        self.get_by_vendor_showtime_id = async_to_streamed_response_wrapper(
            showtimes.get_by_vendor_showtime_id,
        )
