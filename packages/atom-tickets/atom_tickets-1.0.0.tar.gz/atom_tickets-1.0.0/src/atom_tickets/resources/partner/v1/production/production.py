# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .ids import (
    IDsResource,
    AsyncIDsResource,
    IDsResourceWithRawResponse,
    AsyncIDsResourceWithRawResponse,
    IDsResourceWithStreamingResponse,
    AsyncIDsResourceWithStreamingResponse,
)
from .search import (
    SearchResource,
    AsyncSearchResource,
    SearchResourceWithRawResponse,
    AsyncSearchResourceWithRawResponse,
    SearchResourceWithStreamingResponse,
    AsyncSearchResourceWithStreamingResponse,
)
from .details import (
    DetailsResource,
    AsyncDetailsResource,
    DetailsResourceWithRawResponse,
    AsyncDetailsResourceWithRawResponse,
    DetailsResourceWithStreamingResponse,
    AsyncDetailsResourceWithStreamingResponse,
)
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
from .....types.partner.v1.production.production_details import ProductionDetails

__all__ = ["ProductionResource", "AsyncProductionResource"]


class ProductionResource(SyncAPIResource):
    @cached_property
    def ids(self) -> IDsResource:
        return IDsResource(self._client)

    @cached_property
    def details(self) -> DetailsResource:
        return DetailsResource(self._client)

    @cached_property
    def search(self) -> SearchResource:
        return SearchResource(self._client)

    @cached_property
    def with_raw_response(self) -> ProductionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return ProductionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProductionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return ProductionResourceWithStreamingResponse(self)

    def get_by_vendor_production_id(
        self,
        vendor_production_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProductionDetails:
        """
        Returns production details for a vendor-specific production ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vendor_production_id:
            raise ValueError(
                f"Expected a non-empty value for `vendor_production_id` but received {vendor_production_id!r}"
            )
        return self._get(
            f"/partner/v1/productions/byVendorProductionId/{vendor_production_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProductionDetails,
        )


class AsyncProductionResource(AsyncAPIResource):
    @cached_property
    def ids(self) -> AsyncIDsResource:
        return AsyncIDsResource(self._client)

    @cached_property
    def details(self) -> AsyncDetailsResource:
        return AsyncDetailsResource(self._client)

    @cached_property
    def search(self) -> AsyncSearchResource:
        return AsyncSearchResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProductionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncProductionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProductionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncProductionResourceWithStreamingResponse(self)

    async def get_by_vendor_production_id(
        self,
        vendor_production_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProductionDetails:
        """
        Returns production details for a vendor-specific production ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vendor_production_id:
            raise ValueError(
                f"Expected a non-empty value for `vendor_production_id` but received {vendor_production_id!r}"
            )
        return await self._get(
            f"/partner/v1/productions/byVendorProductionId/{vendor_production_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProductionDetails,
        )


class ProductionResourceWithRawResponse:
    def __init__(self, production: ProductionResource) -> None:
        self._production = production

        self.get_by_vendor_production_id = to_raw_response_wrapper(
            production.get_by_vendor_production_id,
        )

    @cached_property
    def ids(self) -> IDsResourceWithRawResponse:
        return IDsResourceWithRawResponse(self._production.ids)

    @cached_property
    def details(self) -> DetailsResourceWithRawResponse:
        return DetailsResourceWithRawResponse(self._production.details)

    @cached_property
    def search(self) -> SearchResourceWithRawResponse:
        return SearchResourceWithRawResponse(self._production.search)


class AsyncProductionResourceWithRawResponse:
    def __init__(self, production: AsyncProductionResource) -> None:
        self._production = production

        self.get_by_vendor_production_id = async_to_raw_response_wrapper(
            production.get_by_vendor_production_id,
        )

    @cached_property
    def ids(self) -> AsyncIDsResourceWithRawResponse:
        return AsyncIDsResourceWithRawResponse(self._production.ids)

    @cached_property
    def details(self) -> AsyncDetailsResourceWithRawResponse:
        return AsyncDetailsResourceWithRawResponse(self._production.details)

    @cached_property
    def search(self) -> AsyncSearchResourceWithRawResponse:
        return AsyncSearchResourceWithRawResponse(self._production.search)


class ProductionResourceWithStreamingResponse:
    def __init__(self, production: ProductionResource) -> None:
        self._production = production

        self.get_by_vendor_production_id = to_streamed_response_wrapper(
            production.get_by_vendor_production_id,
        )

    @cached_property
    def ids(self) -> IDsResourceWithStreamingResponse:
        return IDsResourceWithStreamingResponse(self._production.ids)

    @cached_property
    def details(self) -> DetailsResourceWithStreamingResponse:
        return DetailsResourceWithStreamingResponse(self._production.details)

    @cached_property
    def search(self) -> SearchResourceWithStreamingResponse:
        return SearchResourceWithStreamingResponse(self._production.search)


class AsyncProductionResourceWithStreamingResponse:
    def __init__(self, production: AsyncProductionResource) -> None:
        self._production = production

        self.get_by_vendor_production_id = async_to_streamed_response_wrapper(
            production.get_by_vendor_production_id,
        )

    @cached_property
    def ids(self) -> AsyncIDsResourceWithStreamingResponse:
        return AsyncIDsResourceWithStreamingResponse(self._production.ids)

    @cached_property
    def details(self) -> AsyncDetailsResourceWithStreamingResponse:
        return AsyncDetailsResourceWithStreamingResponse(self._production.details)

    @cached_property
    def search(self) -> AsyncSearchResourceWithStreamingResponse:
        return AsyncSearchResourceWithStreamingResponse(self._production.search)
