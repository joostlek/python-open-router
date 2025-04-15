"""Models for OpenRouter."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime  # noqa: TC003
from enum import IntEnum, IntFlag, StrEnum
from typing import Annotated

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import Discriminator


@dataclass
class KeyDataWrapper(DataClassORJSONMixin):

    data: KeyData

@dataclass
class KeyData(DataClassORJSONMixin):

    label: str
    usage: int
    is_provisioning_key: bool
    limit_remaining: int | None
    is_free_tier: bool
