# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from atom_tickets import AtomTickets, AsyncAtomTickets
from atom_tickets.types.partner.v1.venue import (
    VenueDetails,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDetails:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_ids(self, client: AtomTickets) -> None:
        detail = client.partner.v1.venue.details.get_by_ids(
            ids=["C0057070265"],
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_ids_with_all_params(self, client: AtomTickets) -> None:
        detail = client.partner.v1.venue.details.get_by_ids(
            ids=["C0057070265"],
            location={
                "lat": 34.0195,
                "lon": -118.4912,
            },
            page=0,
            page_size=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_by_ids(self, client: AtomTickets) -> None:
        response = client.partner.v1.venue.details.with_raw_response.get_by_ids(
            ids=["C0057070265"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = response.parse()
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_by_ids(self, client: AtomTickets) -> None:
        with client.partner.v1.venue.details.with_streaming_response.get_by_ids(
            ids=["C0057070265"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = response.parse()
            assert_matches_type(VenueDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_location(self, client: AtomTickets) -> None:
        detail = client.partner.v1.venue.details.get_by_location(
            lat=0,
            lon=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_location_with_all_params(self, client: AtomTickets) -> None:
        detail = client.partner.v1.venue.details.get_by_location(
            lat=0,
            lon=0,
            page=0,
            page_size=0,
            radius=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_by_location(self, client: AtomTickets) -> None:
        response = client.partner.v1.venue.details.with_raw_response.get_by_location(
            lat=0,
            lon=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = response.parse()
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_by_location(self, client: AtomTickets) -> None:
        with client.partner.v1.venue.details.with_streaming_response.get_by_location(
            lat=0,
            lon=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = response.parse()
            assert_matches_type(VenueDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: AtomTickets) -> None:
        detail = client.partner.v1.venue.details.search(
            lat=0,
            lon=0,
            term="term",
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_with_all_params(self, client: AtomTickets) -> None:
        detail = client.partner.v1.venue.details.search(
            lat=0,
            lon=0,
            term="term",
            page=0,
            page_size=0,
            radius=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: AtomTickets) -> None:
        response = client.partner.v1.venue.details.with_raw_response.search(
            lat=0,
            lon=0,
            term="term",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = response.parse()
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: AtomTickets) -> None:
        with client.partner.v1.venue.details.with_streaming_response.search(
            lat=0,
            lon=0,
            term="term",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = response.parse()
            assert_matches_type(VenueDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDetails:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_ids(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.venue.details.get_by_ids(
            ids=["C0057070265"],
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_ids_with_all_params(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.venue.details.get_by_ids(
            ids=["C0057070265"],
            location={
                "lat": 34.0195,
                "lon": -118.4912,
            },
            page=0,
            page_size=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_by_ids(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.venue.details.with_raw_response.get_by_ids(
            ids=["C0057070265"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = await response.parse()
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_by_ids(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.venue.details.with_streaming_response.get_by_ids(
            ids=["C0057070265"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = await response.parse()
            assert_matches_type(VenueDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_location(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.venue.details.get_by_location(
            lat=0,
            lon=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_location_with_all_params(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.venue.details.get_by_location(
            lat=0,
            lon=0,
            page=0,
            page_size=0,
            radius=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_by_location(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.venue.details.with_raw_response.get_by_location(
            lat=0,
            lon=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = await response.parse()
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_by_location(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.venue.details.with_streaming_response.get_by_location(
            lat=0,
            lon=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = await response.parse()
            assert_matches_type(VenueDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.venue.details.search(
            lat=0,
            lon=0,
            term="term",
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.venue.details.search(
            lat=0,
            lon=0,
            term="term",
            page=0,
            page_size=0,
            radius=0,
        )
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.venue.details.with_raw_response.search(
            lat=0,
            lon=0,
            term="term",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = await response.parse()
        assert_matches_type(VenueDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.venue.details.with_streaming_response.search(
            lat=0,
            lon=0,
            term="term",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = await response.parse()
            assert_matches_type(VenueDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True
