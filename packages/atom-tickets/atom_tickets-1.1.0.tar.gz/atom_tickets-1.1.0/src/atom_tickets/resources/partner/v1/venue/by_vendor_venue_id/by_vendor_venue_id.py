# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .showtimes import (
    ShowtimesResource,
    AsyncShowtimesResource,
    ShowtimesResourceWithRawResponse,
    AsyncShowtimesResourceWithRawResponse,
    ShowtimesResourceWithStreamingResponse,
    AsyncShowtimesResourceWithStreamingResponse,
)
from ......_types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......_base_client import make_request_options
from ......types.partner.v1.venue.venue_details import VenueDetails

__all__ = ["ByVendorVenueIDResource", "AsyncByVendorVenueIDResource"]


class ByVendorVenueIDResource(SyncAPIResource):
    @cached_property
    def showtimes(self) -> ShowtimesResource:
        return ShowtimesResource(self._client)

    @cached_property
    def with_raw_response(self) -> ByVendorVenueIDResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return ByVendorVenueIDResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ByVendorVenueIDResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return ByVendorVenueIDResourceWithStreamingResponse(self)

    def get(
        self,
        vendor_venue_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns venue details for a vendor-specific venue ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vendor_venue_id:
            raise ValueError(f"Expected a non-empty value for `vendor_venue_id` but received {vendor_venue_id!r}")
        return self._get(
            f"/partner/v1/venues/byVendorVenueId/{vendor_venue_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VenueDetails,
        )


class AsyncByVendorVenueIDResource(AsyncAPIResource):
    @cached_property
    def showtimes(self) -> AsyncShowtimesResource:
        return AsyncShowtimesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncByVendorVenueIDResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncByVendorVenueIDResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncByVendorVenueIDResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncByVendorVenueIDResourceWithStreamingResponse(self)

    async def get(
        self,
        vendor_venue_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns venue details for a vendor-specific venue ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vendor_venue_id:
            raise ValueError(f"Expected a non-empty value for `vendor_venue_id` but received {vendor_venue_id!r}")
        return await self._get(
            f"/partner/v1/venues/byVendorVenueId/{vendor_venue_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VenueDetails,
        )


class ByVendorVenueIDResourceWithRawResponse:
    def __init__(self, by_vendor_venue_id: ByVendorVenueIDResource) -> None:
        self._by_vendor_venue_id = by_vendor_venue_id

        self.get = to_raw_response_wrapper(
            by_vendor_venue_id.get,
        )

    @cached_property
    def showtimes(self) -> ShowtimesResourceWithRawResponse:
        return ShowtimesResourceWithRawResponse(self._by_vendor_venue_id.showtimes)


class AsyncByVendorVenueIDResourceWithRawResponse:
    def __init__(self, by_vendor_venue_id: AsyncByVendorVenueIDResource) -> None:
        self._by_vendor_venue_id = by_vendor_venue_id

        self.get = async_to_raw_response_wrapper(
            by_vendor_venue_id.get,
        )

    @cached_property
    def showtimes(self) -> AsyncShowtimesResourceWithRawResponse:
        return AsyncShowtimesResourceWithRawResponse(self._by_vendor_venue_id.showtimes)


class ByVendorVenueIDResourceWithStreamingResponse:
    def __init__(self, by_vendor_venue_id: ByVendorVenueIDResource) -> None:
        self._by_vendor_venue_id = by_vendor_venue_id

        self.get = to_streamed_response_wrapper(
            by_vendor_venue_id.get,
        )

    @cached_property
    def showtimes(self) -> ShowtimesResourceWithStreamingResponse:
        return ShowtimesResourceWithStreamingResponse(self._by_vendor_venue_id.showtimes)


class AsyncByVendorVenueIDResourceWithStreamingResponse:
    def __init__(self, by_vendor_venue_id: AsyncByVendorVenueIDResource) -> None:
        self._by_vendor_venue_id = by_vendor_venue_id

        self.get = async_to_streamed_response_wrapper(
            by_vendor_venue_id.get,
        )

    @cached_property
    def showtimes(self) -> AsyncShowtimesResourceWithStreamingResponse:
        return AsyncShowtimesResourceWithStreamingResponse(self._by_vendor_venue_id.showtimes)
