"""Asynchronous Python client for OpenRouter."""


class OpenRouterError(Exception):
    """Generic exception."""


class OpenRouterConnectionError(OpenRouterError):
    """OpenRouter connection exception."""


class OpenRouterAuthenticationError(OpenRouterError):
    """OpenRouter authentication exception."""
