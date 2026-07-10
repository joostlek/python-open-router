"""Tests for the client."""

from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import ClientError
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_PATCH, METH_POST
from aioresponses import CallbackResult, aioresponses
import pytest

from python_open_router import (
    OpenRouterClient,
    OpenRouterConnectionError,
    OpenRouterError,
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


@pytest.mark.parametrize(
    ("endpoint", "fixture", "method"),
    [
        ("key", "key.json", "get_key_data"),
        ("keys", "keys.json", "get_keys"),
        ("models", "models.json", "get_models"),
    ],
    ids=[
        "get_key_data",
        "get_keys",
        "get_models",
    ],
)
async def test_data_retrieval(
    responses: aioresponses,
    client: OpenRouterClient,
    snapshot: SnapshotAssertion,
    endpoint: str,
    fixture: str,
    method: str,
) -> None:
    """Test data retrieval."""
    responses.get(
        f"{MOCK_URL}/{endpoint}",
        status=200,
        body=load_fixture(fixture),
    )
    assert await getattr(client, method)() == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/{endpoint}",
        METH_GET,
        headers=HEADERS,
        params=None,
        json=None,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "name", "limit": 5.0},
        {"name": "name"},
    ],
)
async def test_create_key(
    responses: aioresponses,
    client: OpenRouterClient,
    snapshot: SnapshotAssertion,
    kwargs: dict[str, Any],
) -> None:
    """Test creating a key."""
    responses.post(
        f"{MOCK_URL}/keys",
        status=200,
        body=load_fixture("create_key.json"),
    )
    assert await client.create_key(**kwargs) == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/keys",
        METH_POST,
        headers=HEADERS,
        params=None,
        json=kwargs,
    )


async def test_delete_key(
    responses: aioresponses,
    client: OpenRouterClient,
) -> None:
    """Test deleting a key."""
    responses.delete(
        f"{MOCK_URL}/keys/abcabcabcbababcbabcabcabc",
        status=200,
        body=load_fixture("delete_key.json"),
    )
    result = await client.delete_key("abcabcabcbababcbabcabcabc")
    assert result is True
    responses.assert_called_once_with(
        f"{MOCK_URL}/keys/abcabcabcbababcbabcabcabc",
        METH_DELETE,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_get_key(
    responses: aioresponses,
    client: OpenRouterClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting a single key."""
    responses.get(
        f"{MOCK_URL}/keys/abcabcabcbababcbabcabcabc",
        status=200,
        body=load_fixture("get_key.json"),
    )
    assert await client.get_key("abcabcabcbababcbabcabcabc") == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/keys/abcabcabcbababcbabcabcabc",
        METH_GET,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_update_key(
    responses: aioresponses,
    client: OpenRouterClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test updating a key."""
    responses.patch(
        f"{MOCK_URL}/keys/abcabcabcbababcbabcabcabc",
        status=200,
        body=load_fixture("get_key.json"),
    )
    assert (
        await client.update_key(
            "abcabcabcbababcbabcabcabc", name="New Name", disabled=True
        )
        == snapshot
    )
    responses.assert_called_once_with(
        f"{MOCK_URL}/keys/abcabcabcbababcbabcabcabc",
        METH_PATCH,
        headers=HEADERS,
        params=None,
        json={"name": "New Name", "disabled": True},
    )


async def test_get_model(
    responses: aioresponses,
    client: OpenRouterClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting a single model."""
    responses.get(
        f"{MOCK_URL}/model/amazon/nova-premier-v1",
        status=200,
        body=load_fixture("single_model.json"),
    )
    assert await client.get_model("amazon", "nova-premier-v1") == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/model/amazon/nova-premier-v1",
        METH_GET,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_count_models(
    responses: aioresponses,
    client: OpenRouterClient,
) -> None:
    """Test counting models."""
    responses.get(
        f"{MOCK_URL}/models/count",
        status=200,
        body='{"data": {"count": 100}}',
    )
    result = await client.count_models()
    assert result == 100
    responses.assert_called_once_with(
        f"{MOCK_URL}/models/count",
        METH_GET,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_get_models_with_filters(
    responses: aioresponses,
    client: OpenRouterClient,
) -> None:
    """Test getting models with filter parameters."""
    responses.get(
        re.compile(r"https://openrouter\.ai/api/v1/models\?.*"),
        status=200,
        body=load_fixture("models.json"),
    )
    await client.get_models(
        sort="most-popular",
        q="gpt",
        min_price=0.0,
        max_price=10.0,
    )
    responses.assert_called_once()  # type: ignore[no-untyped-call]


async def test_get_keys_with_filters(
    responses: aioresponses,
    client: OpenRouterClient,
) -> None:
    """Test getting keys with filter parameters."""
    responses.get(
        re.compile(r"https://openrouter\.ai/api/v1/keys\?.*"),
        status=200,
        body=load_fixture("keys.json"),
    )
    await client.get_keys(include_disabled=True, offset=10)
    responses.assert_called_once()  # type: ignore[no-untyped-call]
