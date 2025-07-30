# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from atom_tickets import AtomTickets, AsyncAtomTickets
from atom_tickets.types.partner.v1.venue import VenueDetails

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestByVendorVenueID:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: AtomTickets) -> None:
        by_vendor_venue_id = client.partner.v1.venue.by_vendor_venue_id.get(
            "vendorVenueId",
        )
        assert_matches_type(VenueDetails, by_vendor_venue_id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: AtomTickets) -> None:
        response = client.partner.v1.venue.by_vendor_venue_id.with_raw_response.get(
            "vendorVenueId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        by_vendor_venue_id = response.parse()
        assert_matches_type(VenueDetails, by_vendor_venue_id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: AtomTickets) -> None:
        with client.partner.v1.venue.by_vendor_venue_id.with_streaming_response.get(
            "vendorVenueId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            by_vendor_venue_id = response.parse()
            assert_matches_type(VenueDetails, by_vendor_venue_id, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: AtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vendor_venue_id` but received ''"):
            client.partner.v1.venue.by_vendor_venue_id.with_raw_response.get(
                "",
            )


class TestAsyncByVendorVenueID:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncAtomTickets) -> None:
        by_vendor_venue_id = await async_client.partner.v1.venue.by_vendor_venue_id.get(
            "vendorVenueId",
        )
        assert_matches_type(VenueDetails, by_vendor_venue_id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.venue.by_vendor_venue_id.with_raw_response.get(
            "vendorVenueId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        by_vendor_venue_id = await response.parse()
        assert_matches_type(VenueDetails, by_vendor_venue_id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.venue.by_vendor_venue_id.with_streaming_response.get(
            "vendorVenueId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            by_vendor_venue_id = await response.parse()
            assert_matches_type(VenueDetails, by_vendor_venue_id, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncAtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vendor_venue_id` but received ''"):
            await async_client.partner.v1.venue.by_vendor_venue_id.with_raw_response.get(
                "",
            )
