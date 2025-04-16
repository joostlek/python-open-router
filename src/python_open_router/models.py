"""Models for OpenRouter."""

from __future__ import annotations

from dataclasses import dataclass

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class KeyDataWrapper(DataClassORJSONMixin):
    """Wrapper for OpenRouter key data."""

    data: KeyData


@dataclass
class KeyData(DataClassORJSONMixin):
    """The OpenRouter key data."""

    label: str
    usage: int
    is_provisioning_key: bool
    limit_remaining: int | None
    is_free_tier: bool


@dataclass
class KeysDataWrapper(DataClassORJSONMixin):
    """Wrapper for OpenRouter key data."""

    data: list[Key]


@dataclass
class Key(DataClassORJSONMixin):
    """The OpenRouter key data."""

    hash: str
    name: str
    label: str
    disabled: bool
    limit: int
    usage: int
