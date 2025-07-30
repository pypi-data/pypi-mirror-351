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
from .....types.partner.v1.production import detail_get_by_ids_params
from .....types.partner.v1.production.production_details import ProductionDetails

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
        marketplace_id: Optional[str] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        page_size: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProductionDetails:
        """
        Returns details for specified production IDs

        Args:
          ids: List of production IDs to retrieve

          marketplace_id: Marketplace identifier (US by default)

          page: Page number for results

          page_size: Number of results per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/partner/v1/production/details/byIds",
            body=maybe_transform(
                {
                    "ids": ids,
                    "marketplace_id": marketplace_id,
                    "page": page,
                    "page_size": page_size,
                },
                detail_get_by_ids_params.DetailGetByIDsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProductionDetails,
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
        marketplace_id: Optional[str] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        page_size: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProductionDetails:
        """
        Returns details for specified production IDs

        Args:
          ids: List of production IDs to retrieve

          marketplace_id: Marketplace identifier (US by default)

          page: Page number for results

          page_size: Number of results per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/partner/v1/production/details/byIds",
            body=await async_maybe_transform(
                {
                    "ids": ids,
                    "marketplace_id": marketplace_id,
                    "page": page,
                    "page_size": page_size,
                },
                detail_get_by_ids_params.DetailGetByIDsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProductionDetails,
        )


class DetailsResourceWithRawResponse:
    def __init__(self, details: DetailsResource) -> None:
        self._details = details

        self.get_by_ids = to_raw_response_wrapper(
            details.get_by_ids,
        )


class AsyncDetailsResourceWithRawResponse:
    def __init__(self, details: AsyncDetailsResource) -> None:
        self._details = details

        self.get_by_ids = async_to_raw_response_wrapper(
            details.get_by_ids,
        )


class DetailsResourceWithStreamingResponse:
    def __init__(self, details: DetailsResource) -> None:
        self._details = details

        self.get_by_ids = to_streamed_response_wrapper(
            details.get_by_ids,
        )


class AsyncDetailsResourceWithStreamingResponse:
    def __init__(self, details: AsyncDetailsResource) -> None:
        self._details = details

        self.get_by_ids = async_to_streamed_response_wrapper(
            details.get_by_ids,
        )
