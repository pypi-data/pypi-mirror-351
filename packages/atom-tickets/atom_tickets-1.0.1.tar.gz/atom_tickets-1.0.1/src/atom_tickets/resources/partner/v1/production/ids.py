# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
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
from .....types.partner.v1.production import id_get_by_venue_params
from .....types.partner.v1.production.id_get_by_venue_response import IDGetByVenueResponse

__all__ = ["IDsResource", "AsyncIDsResource"]


class IDsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IDsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return IDsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IDsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return IDsResourceWithStreamingResponse(self)

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
    ) -> IDGetByVenueResponse:
        """
        Returns production IDs available at a specified venue

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
            f"/partner/v1/production/ids/byVenue/{venue_id}",
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
                    id_get_by_venue_params.IDGetByVenueParams,
                ),
            ),
            cast_to=IDGetByVenueResponse,
        )


class AsyncIDsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIDsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncIDsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIDsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncIDsResourceWithStreamingResponse(self)

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
    ) -> IDGetByVenueResponse:
        """
        Returns production IDs available at a specified venue

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
            f"/partner/v1/production/ids/byVenue/{venue_id}",
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
                    id_get_by_venue_params.IDGetByVenueParams,
                ),
            ),
            cast_to=IDGetByVenueResponse,
        )


class IDsResourceWithRawResponse:
    def __init__(self, ids: IDsResource) -> None:
        self._ids = ids

        self.get_by_venue = to_raw_response_wrapper(
            ids.get_by_venue,
        )


class AsyncIDsResourceWithRawResponse:
    def __init__(self, ids: AsyncIDsResource) -> None:
        self._ids = ids

        self.get_by_venue = async_to_raw_response_wrapper(
            ids.get_by_venue,
        )


class IDsResourceWithStreamingResponse:
    def __init__(self, ids: IDsResource) -> None:
        self._ids = ids

        self.get_by_venue = to_streamed_response_wrapper(
            ids.get_by_venue,
        )


class AsyncIDsResourceWithStreamingResponse:
    def __init__(self, ids: AsyncIDsResource) -> None:
        self._ids = ids

        self.get_by_venue = async_to_streamed_response_wrapper(
            ids.get_by_venue,
        )
