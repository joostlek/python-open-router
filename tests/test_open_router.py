"""Tests for the client."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import ClientError
from aiohttp.hdrs import METH_GET, METH_POST
from aioresponses import CallbackResult, aioresponses
import pytest

from python_open_router import (
    OpenRouterClient,
    OpenRouterError,
    OpenRouterConnectionError,
)
from tests import load_fixture
from tests.const import HEADERS, MOCK_URL

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


async def test_putting_in_own_session(
    responses: aioresponses,
) -> None:
    """Test putting in own session."""
    responses.get(
        f"{MOCK_URL}/key",
        status=200,
        body=load_fixture("key.json"),
    )
    async with aiohttp.ClientSession() as session:
        open_router = OpenRouterClient("abc", session=session)
        await open_router.get_key_data()
        assert open_router.session is not None
        assert not open_router.session.closed
        await open_router.close()
        assert not open_router.session.closed


async def test_creating_own_session(
    responses: aioresponses,
) -> None:
    """Test creating own session."""
    responses.get(
        f"{MOCK_URL}/key",
        status=200,
        body=load_fixture("key.json"),
    )
    open_router = OpenRouterClient("abc")
    await open_router.get_key_data()
    assert open_router.session is not None
    assert not open_router.session.closed
    await open_router.close()
    assert open_router.session.closed


async def test_unexpected_server_response(
    responses: aioresponses,
    client: OpenRouterClient,
) -> None:
    """Test handling unexpected response."""
    responses.get(
        f"{MOCK_URL}/key",
        status=404,
        headers={"Content-Type": "plain/text"},
        body="Yes",
    )
    with pytest.raises(OpenRouterError):
        await client.get_key_data()


async def test_timeout(
    responses: aioresponses,
) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return CallbackResult(body="Goodmorning!")

    responses.get(
        f"{MOCK_URL}/key",
        callback=response_handler,
    )
    async with OpenRouterClient(
        "abc",
        request_timeout=1,
    ) as open_router:
        with pytest.raises(OpenRouterConnectionError):
            await open_router.get_key_data()


async def test_client_error(
    client: OpenRouterClient,
    responses: aioresponses,
) -> None:
    """Test client error."""

    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        raise ClientError

    responses.get(
        f"{MOCK_URL}/request/count",
        callback=response_handler,
    )
    with pytest.raises(OpenRouterConnectionError):
        await client.get_key_data()

