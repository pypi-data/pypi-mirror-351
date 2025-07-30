# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.partner.v1.venue import detail_search_params, detail_get_by_ids_params, detail_get_by_location_params
from .....types.partner.v1.venue.venue_details import VenueDetails

__all__ = ["DetailsResource", "AsyncDetailsResource"]


class DetailsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DetailsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return DetailsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DetailsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return DetailsResourceWithStreamingResponse(self)

    def get_by_ids(
        self,
        *,
        ids: List[str],
        location: Optional[detail_get_by_ids_params.Location] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        page_size: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns details for specified venue IDs

        Args:
          ids: List of venue IDs to retrieve

          location: Location to calculate distance from

          page: Page number for results

          page_size: Number of results per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/partner/v1/venue/details/byIds",
            body=maybe_transform(
                {
                    "ids": ids,
                    "location": location,
                    "page": page,
                    "page_size": page_size,
                },
                detail_get_by_ids_params.DetailGetByIDsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VenueDetails,
        )

    def get_by_location(
        self,
        *,
        lat: float,
        lon: float,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        radius: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns venues near a specified geographic location

        Args:
          lat: Latitude coordinate

          lon: Longitude coordinate

          page: Page number for results

          page_size: Number of results per page (max 100)

          radius: Search radius in kilometers (max 80km)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/partner/v1/venue/details/byLocation",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "lat": lat,
                        "lon": lon,
                        "page": page,
                        "page_size": page_size,
                        "radius": radius,
                    },
                    detail_get_by_location_params.DetailGetByLocationParams,
                ),
            ),
            cast_to=VenueDetails,
        )

    def search(
        self,
        *,
        lat: float,
        lon: float,
        term: str,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        radius: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns venues matching a search term near a location

        Args:
          lat: Latitude coordinate

          lon: Longitude coordinate

          term: Search term

          page: Page number for results

          page_size: Number of results per page (max 100)

          radius: Search radius in kilometers (max 80km)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/partner/v1/venue/details/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "lat": lat,
                        "lon": lon,
                        "term": term,
                        "page": page,
                        "page_size": page_size,
                        "radius": radius,
                    },
                    detail_search_params.DetailSearchParams,
                ),
            ),
            cast_to=VenueDetails,
        )


class AsyncDetailsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDetailsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncDetailsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDetailsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncDetailsResourceWithStreamingResponse(self)

    async def get_by_ids(
        self,
        *,
        ids: List[str],
        location: Optional[detail_get_by_ids_params.Location] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        page_size: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns details for specified venue IDs

        Args:
          ids: List of venue IDs to retrieve

          location: Location to calculate distance from

          page: Page number for results

          page_size: Number of results per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/partner/v1/venue/details/byIds",
            body=await async_maybe_transform(
                {
                    "ids": ids,
                    "location": location,
                    "page": page,
                    "page_size": page_size,
                },
                detail_get_by_ids_params.DetailGetByIDsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VenueDetails,
        )

    async def get_by_location(
        self,
        *,
        lat: float,
        lon: float,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        radius: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns venues near a specified geographic location

        Args:
          lat: Latitude coordinate

          lon: Longitude coordinate

          page: Page number for results

          page_size: Number of results per page (max 100)

          radius: Search radius in kilometers (max 80km)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/partner/v1/venue/details/byLocation",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "lat": lat,
                        "lon": lon,
                        "page": page,
                        "page_size": page_size,
                        "radius": radius,
                    },
                    detail_get_by_location_params.DetailGetByLocationParams,
                ),
            ),
            cast_to=VenueDetails,
        )

    async def search(
        self,
        *,
        lat: float,
        lon: float,
        term: str,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        radius: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VenueDetails:
        """
        Returns venues matching a search term near a location

        Args:
          lat: Latitude coordinate

          lon: Longitude coordinate

          term: Search term

          page: Page number for results

          page_size: Number of results per page (max 100)

          radius: Search radius in kilometers (max 80km)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/partner/v1/venue/details/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "lat": lat,
                        "lon": lon,
                        "term": term,
                        "page": page,
                        "page_size": page_size,
                        "radius": radius,
                    },
                    detail_search_params.DetailSearchParams,
                ),
            ),
            cast_to=VenueDetails,
        )


class DetailsResourceWithRawResponse:
    def __init__(self, details: DetailsResource) -> None:
        self._details = details

        self.get_by_ids = to_raw_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_location = to_raw_response_wrapper(
            details.get_by_location,
        )
        self.search = to_raw_response_wrapper(
            details.search,
        )


class AsyncDetailsResourceWithRawResponse:
    def __init__(self, details: AsyncDetailsResource) -> None:
        self._details = details

        self.get_by_ids = async_to_raw_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_location = async_to_raw_response_wrapper(
            details.get_by_location,
        )
        self.search = async_to_raw_response_wrapper(
            details.search,
        )


class DetailsResourceWithStreamingResponse:
    def __init__(self, details: DetailsResource) -> None:
        self._details = details

        self.get_by_ids = to_streamed_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_location = to_streamed_response_wrapper(
            details.get_by_location,
        )
        self.search = to_streamed_response_wrapper(
            details.search,
        )


class AsyncDetailsResourceWithStreamingResponse:
    def __init__(self, details: AsyncDetailsResource) -> None:
        self._details = details

        self.get_by_ids = async_to_streamed_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_location = async_to_streamed_response_wrapper(
            details.get_by_location,
        )
        self.search = async_to_streamed_response_wrapper(
            details.search,
        )
