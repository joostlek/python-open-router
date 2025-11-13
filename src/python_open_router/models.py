"""Models for OpenRouter."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import logging
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin

_LOGGER = logging.getLogger(__package__)


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
class CreateKeyDataWrapper(DataClassORJSONMixin):
    """Wrapper for OpenRouter key data."""

    data: CreatedKey


@dataclass
class Key(DataClassORJSONMixin):
    """The OpenRouter key data."""

    hash: str
    name: str
    label: str
    disabled: bool
    limit: float
    usage: float = 0.0


@dataclass(kw_only=True)
class CreatedKey(Key):
    """Created key."""

    key: str


@dataclass
class ModelsDataWrapper(DataClassORJSONMixin):
    """Wrapper for OpenRouter model data."""

    data: list[Model]


class SupportedParameter(StrEnum):
    """Supported parameters for models."""

    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    MAX_TOKENS = "max_tokens"
    REASONING = "reasoning"
    INCLUDE_REASONING = "include_reasoning"
    STOP = "stop"
    TOK_K = "top_k"
    SEED = "seed"
    RESPONSE_FORMAT = "response_format"
    TOOLS = "tools"
    TOOL_CHOICE = "tool_choice"
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    MIN_P = "min_p"
    REPETITION_PENALTY = "repetition_penalty"
    LOGPROBS = "logprobs"
    LOGIT_BIAS = "logit_bias"
    TOP_LOGPROBS = "top_logprobs"
    STRUCTURED_OUTPUTS = "structured_outputs"
    WEB_SEARCH_OPTIONS = "web_search_options"
    TOP_A = "top_a"


class Modality(StrEnum):
    """Supported modalities for models."""

    AUDIO = "audio"
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    EMBEDDINGS = "embeddings"
    VIDEO = "video"


@dataclass(kw_only=True)
class ModelArchitecture(DataClassORJSONMixin):
    """Model data."""

    input_modalities: list[Modality]
    output_modalities: list[Modality]


@dataclass(kw_only=True)
class Model(DataClassORJSONMixin):
    """Model data."""

    id: str
    canonical_slug: str
    hugging_face_id: str | None
    name: str
    description: str
    context_length: int
    architecture: ModelArchitecture
    supported_parameters: list[SupportedParameter]

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Pre deserialize hook."""
        parameters = d.get("supported_parameters", [])
        for parameter in parameters:
            if parameter not in SupportedParameter:
                _LOGGER.warning(
                    "Unsupported parameter: %s. Please report at https://github.com/joostlek/python-open-router/issues.",
                    parameter,
                )
                parameters.remove(parameter)
        return d

    @classmethod
    def __post_deserialize__(cls, obj: Model) -> Model:
        """Post deserialize hook."""
        if obj.hugging_face_id == "":
            obj.hugging_face_id = None
        return obj
