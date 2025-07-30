# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from atom_tickets import AtomTickets, AsyncAtomTickets
from atom_tickets.types.partner.v1.showtime import ShowtimeDetails

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestShowtimes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_vendor_showtime_id(self, client: AtomTickets) -> None:
        showtime = client.partner.v1.venue.showtimes.get_by_vendor_showtime_id(
            vendor_showtime_id="vendorShowtimeId",
            venue_id="venueId",
        )
        assert_matches_type(ShowtimeDetails, showtime, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_by_vendor_showtime_id(self, client: AtomTickets) -> None:
        response = client.partner.v1.venue.showtimes.with_raw_response.get_by_vendor_showtime_id(
            vendor_showtime_id="vendorShowtimeId",
            venue_id="venueId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        showtime = response.parse()
        assert_matches_type(ShowtimeDetails, showtime, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_by_vendor_showtime_id(self, client: AtomTickets) -> None:
        with client.partner.v1.venue.showtimes.with_streaming_response.get_by_vendor_showtime_id(
            vendor_showtime_id="vendorShowtimeId",
            venue_id="venueId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            showtime = response.parse()
            assert_matches_type(ShowtimeDetails, showtime, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_by_vendor_showtime_id(self, client: AtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `venue_id` but received ''"):
            client.partner.v1.venue.showtimes.with_raw_response.get_by_vendor_showtime_id(
                vendor_showtime_id="vendorShowtimeId",
                venue_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vendor_showtime_id` but received ''"):
            client.partner.v1.venue.showtimes.with_raw_response.get_by_vendor_showtime_id(
                vendor_showtime_id="",
                venue_id="venueId",
            )


class TestAsyncShowtimes:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_vendor_showtime_id(self, async_client: AsyncAtomTickets) -> None:
        showtime = await async_client.partner.v1.venue.showtimes.get_by_vendor_showtime_id(
            vendor_showtime_id="vendorShowtimeId",
            venue_id="venueId",
        )
        assert_matches_type(ShowtimeDetails, showtime, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_by_vendor_showtime_id(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.venue.showtimes.with_raw_response.get_by_vendor_showtime_id(
            vendor_showtime_id="vendorShowtimeId",
            venue_id="venueId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        showtime = await response.parse()
        assert_matches_type(ShowtimeDetails, showtime, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_by_vendor_showtime_id(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.venue.showtimes.with_streaming_response.get_by_vendor_showtime_id(
            vendor_showtime_id="vendorShowtimeId",
            venue_id="venueId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            showtime = await response.parse()
            assert_matches_type(ShowtimeDetails, showtime, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_by_vendor_showtime_id(self, async_client: AsyncAtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `venue_id` but received ''"):
            await async_client.partner.v1.venue.showtimes.with_raw_response.get_by_vendor_showtime_id(
                vendor_showtime_id="vendorShowtimeId",
                venue_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vendor_showtime_id` but received ''"):
            await async_client.partner.v1.venue.showtimes.with_raw_response.get_by_vendor_showtime_id(
                vendor_showtime_id="",
                venue_id="venueId",
            )
