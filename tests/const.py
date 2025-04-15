"""Constants for tests."""

from importlib import metadata

MOCK_URL = "https://openrouter.ai/api/v1"
version = metadata.version("python_open_router")

HEADERS = {
    "User-Agent": f"PythonOpenRouter/{version}",
    "Accept": "application/json",
    "Authorization": "Bearer key",
}
