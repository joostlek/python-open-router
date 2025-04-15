"""Asynchronous Python client for OpenRouter."""

from collections.abc import AsyncGenerator, Generator

from aiohttp import ClientSession
from aioresponses import aioresponses
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
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
