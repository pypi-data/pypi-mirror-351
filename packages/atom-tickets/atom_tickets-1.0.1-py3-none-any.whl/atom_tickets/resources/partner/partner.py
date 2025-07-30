# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .v1.v1 import (
    V1Resource,
    AsyncV1Resource,
    V1ResourceWithRawResponse,
    AsyncV1ResourceWithRawResponse,
    V1ResourceWithStreamingResponse,
    AsyncV1ResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["PartnerResource", "AsyncPartnerResource"]


class PartnerResource(SyncAPIResource):
    @cached_property
    def v1(self) -> V1Resource:
        return V1Resource(self._client)

    @cached_property
    def with_raw_response(self) -> PartnerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return PartnerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PartnerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return PartnerResourceWithStreamingResponse(self)

    def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Health check endpoint to validate API availability"""
        return self._get(
            "/partner/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncPartnerResource(AsyncAPIResource):
    @cached_property
    def v1(self) -> AsyncV1Resource:
        return AsyncV1Resource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPartnerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AtomTickets/discovery-search#accessing-raw-response-data-eg-headers
        """
        return AsyncPartnerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPartnerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AtomTickets/discovery-search#with_streaming_response
        """
        return AsyncPartnerResourceWithStreamingResponse(self)

    async def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Health check endpoint to validate API availability"""
        return await self._get(
            "/partner/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class PartnerResourceWithRawResponse:
    def __init__(self, partner: PartnerResource) -> None:
        self._partner = partner

        self.ping = to_raw_response_wrapper(
            partner.ping,
        )

    @cached_property
    def v1(self) -> V1ResourceWithRawResponse:
        return V1ResourceWithRawResponse(self._partner.v1)


class AsyncPartnerResourceWithRawResponse:
    def __init__(self, partner: AsyncPartnerResource) -> None:
        self._partner = partner

        self.ping = async_to_raw_response_wrapper(
            partner.ping,
        )

    @cached_property
    def v1(self) -> AsyncV1ResourceWithRawResponse:
        return AsyncV1ResourceWithRawResponse(self._partner.v1)


class PartnerResourceWithStreamingResponse:
    def __init__(self, partner: PartnerResource) -> None:
        self._partner = partner

        self.ping = to_streamed_response_wrapper(
            partner.ping,
        )

    @cached_property
    def v1(self) -> V1ResourceWithStreamingResponse:
        return V1ResourceWithStreamingResponse(self._partner.v1)


class AsyncPartnerResourceWithStreamingResponse:
    def __init__(self, partner: AsyncPartnerResource) -> None:
        self._partner = partner

        self.ping = async_to_streamed_response_wrapper(
            partner.ping,
        )

    @cached_property
    def v1(self) -> AsyncV1ResourceWithStreamingResponse:
        return AsyncV1ResourceWithStreamingResponse(self._partner.v1)
