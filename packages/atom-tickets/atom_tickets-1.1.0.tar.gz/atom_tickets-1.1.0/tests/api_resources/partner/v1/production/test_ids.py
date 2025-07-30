# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from atom_tickets import AtomTickets, AsyncAtomTickets
from atom_tickets._utils import parse_datetime
from atom_tickets.types.partner.v1.production import IDGetByVenueResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIDs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_by_venue(self, client: AtomTickets) -> None:
        id = client.partner.v1.production.ids.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(IDGetByVenueResponse, id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_by_venue(self, client: AtomTickets) -> None:
        response = client.partner.v1.production.ids.with_raw_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        id = response.parse()
        assert_matches_type(IDGetByVenueResponse, id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_by_venue(self, client: AtomTickets) -> None:
        with client.partner.v1.production.ids.with_streaming_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            id = response.parse()
            assert_matches_type(IDGetByVenueResponse, id, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_by_venue(self, client: AtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `venue_id` but received ''"):
            client.partner.v1.production.ids.with_raw_response.get_by_venue(
                venue_id="",
                iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
                iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            )


class TestAsyncIDs:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        id = await async_client.partner.v1.production.ids.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(IDGetByVenueResponse, id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        response = await async_client.partner.v1.production.ids.with_raw_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        id = await response.parse()
        assert_matches_type(IDGetByVenueResponse, id, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        async with async_client.partner.v1.production.ids.with_streaming_response.get_by_venue(
            venue_id="venueId",
            iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            id = await response.parse()
            assert_matches_type(IDGetByVenueResponse, id, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_by_venue(self, async_client: AsyncAtomTickets) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `venue_id` but received ''"):
            await async_client.partner.v1.production.ids.with_raw_response.get_by_venue(
                venue_id="",
                iso_end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
                iso_start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            )
