"""Asynchronous Python client for OpenRouter."""

from collections.abc import AsyncGenerator

from aiohttp import ClientSession
from aiointercept import aiointercept
import pytest

from python_open_router import OpenRouterClient
from syrupy import SnapshotAssertion

from .syrupy import OpenRouterSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the OpenRouter extension."""
    return snapshot.use_extension(OpenRouterSnapshotExtension)


@pytest.fixture
async def client() -> AsyncGenerator[OpenRouterClient, None]:
    """Return an OpenRouter client."""
    async with (
        ClientSession() as session,
        OpenRouterClient(
            "key",
            session=session,
        ) as open_router_client,
    ):
        yield open_router_client


@pytest.fixture(name="responses")
async def aiointercept_fixture() -> AsyncGenerator[aiointercept, None]:
    """Return aiointercept fixture."""
    async with aiointercept(mock_external_urls=True) as mocked_responses:
        yield mocked_responses
