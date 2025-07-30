# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime

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
from .....types.partner.v1.showtime import (
    detail_get_by_ids_params,
    detail_get_by_venue_params,
    detail_get_for_multiple_venues_params,
)
from .....types.partner.v1.showtime.showtime_details import ShowtimeDetails
from .....types.partner.v1.showtime.detail_get_for_multiple_venues_response import DetailGetForMultipleVenuesResponse

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
        page: Optional[int] | NotGiven = NOT_GIVEN,
        page_size: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ShowtimeDetails:
        """
        Returns details for specified showtime IDs

        Args:
          ids: List of showtime IDs to retrieve

          page: Page number for results

          page_size: Number of results per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/partner/v1/showtime/details/byIds",
            body=maybe_transform(
                {
                    "ids": ids,
                    "page": page,
                    "page_size": page_size,
                },
                detail_get_by_ids_params.DetailGetByIDsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShowtimeDetails,
        )

    def get_by_venue(
        self,
        venue_id: str,
        *,
        iso_end_date: Union[str, datetime],
        iso_start_date: Union[str, datetime],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ShowtimeDetails:
        """
        Returns showtime details for a specified venue

        Args:
          iso_end_date: ISO8601 formatted end date without milliseconds

          iso_start_date: ISO8601 formatted start date without milliseconds

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not venue_id:
            raise ValueError(f"Expected a non-empty value for `venue_id` but received {venue_id!r}")
        return self._get(
            f"/partner/v1/showtime/details/byVenue/{venue_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "iso_end_date": iso_end_date,
                        "iso_start_date": iso_start_date,
                    },
                    detail_get_by_venue_params.DetailGetByVenueParams,
                ),
            ),
            cast_to=ShowtimeDetails,
        )

    def get_for_multiple_venues(
        self,
        *,
        venue_ids: List[str],
        include_production_details: Optional[bool] | NotGiven = NOT_GIVEN,
        iso_date_bounds: Optional[detail_get_for_multiple_venues_params.ISODateBounds] | NotGiven = NOT_GIVEN,
        local_date_bounds: Optional[detail_get_for_multiple_venues_params.LocalDateBounds] | NotGiven = NOT_GIVEN,
        marketplace_id: Optional[str] | NotGiven = NOT_GIVEN,
        production_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DetailGetForMultipleVenuesResponse:
        """
        Returns showtime details for multiple venues

        Args:
          venue_ids: Set of venue IDs to retrieve showtimes for

          include_production_details: Whether to include production details in response

          iso_date_bounds: Date bounds in ISO format

          local_date_bounds: Date bounds in local format

          marketplace_id: Marketplace identifier

          production_ids: Set of production IDs to filter showtimes by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/partner/v1/showtime/details/forVenues",
            body=maybe_transform(
                {
                    "venue_ids": venue_ids,
                    "include_production_details": include_production_details,
                    "iso_date_bounds": iso_date_bounds,
                    "local_date_bounds": local_date_bounds,
                    "marketplace_id": marketplace_id,
                    "production_ids": production_ids,
                },
                detail_get_for_multiple_venues_params.DetailGetForMultipleVenuesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DetailGetForMultipleVenuesResponse,
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
        page: Optional[int] | NotGiven = NOT_GIVEN,
        page_size: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ShowtimeDetails:
        """
        Returns details for specified showtime IDs

        Args:
          ids: List of showtime IDs to retrieve

          page: Page number for results

          page_size: Number of results per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/partner/v1/showtime/details/byIds",
            body=await async_maybe_transform(
                {
                    "ids": ids,
                    "page": page,
                    "page_size": page_size,
                },
                detail_get_by_ids_params.DetailGetByIDsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShowtimeDetails,
        )

    async def get_by_venue(
        self,
        venue_id: str,
        *,
        iso_end_date: Union[str, datetime],
        iso_start_date: Union[str, datetime],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ShowtimeDetails:
        """
        Returns showtime details for a specified venue

        Args:
          iso_end_date: ISO8601 formatted end date without milliseconds

          iso_start_date: ISO8601 formatted start date without milliseconds

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not venue_id:
            raise ValueError(f"Expected a non-empty value for `venue_id` but received {venue_id!r}")
        return await self._get(
            f"/partner/v1/showtime/details/byVenue/{venue_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "iso_end_date": iso_end_date,
                        "iso_start_date": iso_start_date,
                    },
                    detail_get_by_venue_params.DetailGetByVenueParams,
                ),
            ),
            cast_to=ShowtimeDetails,
        )

    async def get_for_multiple_venues(
        self,
        *,
        venue_ids: List[str],
        include_production_details: Optional[bool] | NotGiven = NOT_GIVEN,
        iso_date_bounds: Optional[detail_get_for_multiple_venues_params.ISODateBounds] | NotGiven = NOT_GIVEN,
        local_date_bounds: Optional[detail_get_for_multiple_venues_params.LocalDateBounds] | NotGiven = NOT_GIVEN,
        marketplace_id: Optional[str] | NotGiven = NOT_GIVEN,
        production_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DetailGetForMultipleVenuesResponse:
        """
        Returns showtime details for multiple venues

        Args:
          venue_ids: Set of venue IDs to retrieve showtimes for

          include_production_details: Whether to include production details in response

          iso_date_bounds: Date bounds in ISO format

          local_date_bounds: Date bounds in local format

          marketplace_id: Marketplace identifier

          production_ids: Set of production IDs to filter showtimes by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/partner/v1/showtime/details/forVenues",
            body=await async_maybe_transform(
                {
                    "venue_ids": venue_ids,
                    "include_production_details": include_production_details,
                    "iso_date_bounds": iso_date_bounds,
                    "local_date_bounds": local_date_bounds,
                    "marketplace_id": marketplace_id,
                    "production_ids": production_ids,
                },
                detail_get_for_multiple_venues_params.DetailGetForMultipleVenuesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DetailGetForMultipleVenuesResponse,
        )


class DetailsResourceWithRawResponse:
    def __init__(self, details: DetailsResource) -> None:
        self._details = details

        self.get_by_ids = to_raw_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_venue = to_raw_response_wrapper(
            details.get_by_venue,
        )
        self.get_for_multiple_venues = to_raw_response_wrapper(
            details.get_for_multiple_venues,
        )


class AsyncDetailsResourceWithRawResponse:
    def __init__(self, details: AsyncDetailsResource) -> None:
        self._details = details

        self.get_by_ids = async_to_raw_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_venue = async_to_raw_response_wrapper(
            details.get_by_venue,
        )
        self.get_for_multiple_venues = async_to_raw_response_wrapper(
            details.get_for_multiple_venues,
        )


class DetailsResourceWithStreamingResponse:
    def __init__(self, details: DetailsResource) -> None:
        self._details = details

        self.get_by_ids = to_streamed_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_venue = to_streamed_response_wrapper(
            details.get_by_venue,
        )
        self.get_for_multiple_venues = to_streamed_response_wrapper(
            details.get_for_multiple_venues,
        )


class AsyncDetailsResourceWithStreamingResponse:
    def __init__(self, details: AsyncDetailsResource) -> None:
        self._details = details

        self.get_by_ids = async_to_streamed_response_wrapper(
            details.get_by_ids,
        )
        self.get_by_venue = async_to_streamed_response_wrapper(
            details.get_by_venue,
        )
        self.get_for_multiple_venues = async_to_streamed_response_wrapper(
            details.get_for_multiple_venues,
        )
