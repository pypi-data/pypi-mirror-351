# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from atom_tickets import AtomTickets, AsyncAtomTickets
from atom_tickets._utils import parse_datetime
from atom_tickets.types.partner.v1.showtime import (
    ShowtimeDetails,
    DetailGetForMultipleVenuesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDetails:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_ids(self, client: AtomTickets) -> None:
        detail = client.partner.v1.showtime.details.get_by_ids(
            ids=["D00747321039"],
        )
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_ids_with_all_params(self, client: AtomTickets) -> None:
        detail = client.partner.v1.showtime.details.get_by_ids(
            ids=["D00747321039"],
            page=0,
            page_size=0,
        )
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_by_ids(self, client: AtomTickets) -> None:
        response = client.partner.v1.showtime.details.with_raw_response.get_by_ids(
            ids=["D00747321039"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = response.parse()
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_by_ids(self, client: AtomTickets) -> None:
        with client.partner.v1.showtime.details.with_streaming_response.get_by_ids(
            ids=["D00747321039"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = response.parse()
            assert_matches_type(ShowtimeDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_venue(self, client: AtomTickets) -> None:
        detail = client.partner.v1.showtime.details.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_by_venue(self, client: AtomTickets) -> None:
        response = client.partner.v1.showtime.details.with_raw_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = response.parse()
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_by_venue(self, client: AtomTickets) -> None:
        with client.partner.v1.showtime.details.with_streaming_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = response.parse()
            assert_matches_type(ShowtimeDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_by_venue(self, client: AtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `venue_id` but received ''"):
            client.partner.v1.showtime.details.with_raw_response.get_by_venue(
                venue_id="",
                iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
                iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_for_multiple_venues(self, client: AtomTickets) -> None:
        detail = client.partner.v1.showtime.details.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
        )
        assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_for_multiple_venues_with_all_params(self, client: AtomTickets) -> None:
        detail = client.partner.v1.showtime.details.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
            include_production_details=True,
            iso_date_bounds={
                "iso_end_date": parse_datetime("2019-02-26T07:00:00Z"),
                "iso_start_date": parse_datetime("2019-02-25T07:00:00Z"),
            },
            local_date_bounds={
                "local_end_date": "localEndDate",
                "local_start_date": "localStartDate",
            },
            marketplace_id="marketplaceId",
            production_ids=["string"],
        )
        assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_for_multiple_venues(self, client: AtomTickets) -> None:
        response = client.partner.v1.showtime.details.with_raw_response.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = response.parse()
        assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_for_multiple_venues(self, client: AtomTickets) -> None:
        with client.partner.v1.showtime.details.with_streaming_response.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = response.parse()
            assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDetails:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_ids(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.showtime.details.get_by_ids(
            ids=["D00747321039"],
        )
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_ids_with_all_params(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.showtime.details.get_by_ids(
            ids=["D00747321039"],
            page=0,
            page_size=0,
        )
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_by_ids(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.showtime.details.with_raw_response.get_by_ids(
            ids=["D00747321039"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = await response.parse()
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_by_ids(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.showtime.details.with_streaming_response.get_by_ids(
            ids=["D00747321039"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = await response.parse()
            assert_matches_type(ShowtimeDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.showtime.details.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.showtime.details.with_raw_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = await response.parse()
        assert_matches_type(ShowtimeDetails, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.showtime.details.with_streaming_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = await response.parse()
            assert_matches_type(ShowtimeDetails, detail, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `venue_id` but received ''"):
            await async_client.partner.v1.showtime.details.with_raw_response.get_by_venue(
                venue_id="",
                iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
                iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_for_multiple_venues(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.showtime.details.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
        )
        assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_for_multiple_venues_with_all_params(self, async_client: AsyncAtomTickets) -> None:
        detail = await async_client.partner.v1.showtime.details.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
            include_production_details=True,
            iso_date_bounds={
                "iso_end_date": parse_datetime("2019-02-26T07:00:00Z"),
                "iso_start_date": parse_datetime("2019-02-25T07:00:00Z"),
            },
            local_date_bounds={
                "local_end_date": "localEndDate",
                "local_start_date": "localStartDate",
            },
            marketplace_id="marketplaceId",
            production_ids=["string"],
        )
        assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_for_multiple_venues(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.showtime.details.with_raw_response.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        detail = await response.parse()
        assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_for_multiple_venues(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.showtime.details.with_streaming_response.get_for_multiple_venues(
            venue_ids=["C0057070265", "C00110921804", "C00401723167", "C00928817799"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            detail = await response.parse()
            assert_matches_type(DetailGetForMultipleVenuesResponse, detail, path=["response"])

        assert cast(Any, response.is_closed) is True
