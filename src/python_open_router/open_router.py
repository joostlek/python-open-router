"""Asynchronous Python client for Open Router."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
import socket
from typing import TYPE_CHECKING, Any

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from python_open_router.exceptions import OpenRouterConnectionError
from python_open_router.models import KeyData, KeyDataWrapper

if TYPE_CHECKING:
    from typing_extensions import Self


VERSION = metadata.version(__package__)
HOST = "openrouter.ai"


@dataclass
class OpenRouterClient:
    """Main class for handling connections with OpenRouter."""

    api_key: str
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        method: str,
        uri: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to OpenRouter."""
        url = URL.build(host=HOST, scheme="https").joinpath(f"api/v1/{uri}")

        headers = {
            "User-Agent": f"PythonOpenRouter/{VERSION}",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    json=data,
                )
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the service"
            raise OpenRouterConnectionError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with the service"
            raise OpenRouterConnectionError(msg) from exception

        if response.status >= 400:
            content_type = response.headers.get("Content-Type", "")
            text = await response.text()
            msg = "Unexpected response from OpenRouter"
            raise OpenRouterConnectionError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.text()

    async def get_key_data(self) -> KeyData:
        """Get key data for API key."""
        response = await self._request(METH_GET, "key")
        return KeyDataWrapper.from_json(response).data

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The OpenRouterClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
