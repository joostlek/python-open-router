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
    usage: float
    is_provisioning_key: bool
    limit_remaining: float | None
    is_free_tier: bool
    limit: float | None = None
    limit_reset: str | None = None
    usage_daily: float = 0.0
    usage_weekly: float = 0.0
    usage_monthly: float = 0.0
    byok_usage: float = 0.0
    byok_usage_daily: float = 0.0
    byok_usage_weekly: float = 0.0
    byok_usage_monthly: float = 0.0
    include_byok_in_limit: bool = False
    is_management_key: bool = False
    creator_user_id: str | None = None
    expires_at: str | None = None


@dataclass
class KeysDataWrapper(DataClassORJSONMixin):
    """Wrapper for OpenRouter key data."""

    data: list[Key]


@dataclass
class KeyCreateResponse(DataClassORJSONMixin):
    """Response from creating a key."""

    data: Key
    key: str


@dataclass
class Key(DataClassORJSONMixin):
    """The OpenRouter key data."""

    hash: str
    name: str
    label: str
    disabled: bool
    limit: float | None = None
    usage: float = 0.0
    created_at: str = ""
    updated_at: str | None = None
    limit_remaining: float | None = None
    limit_reset: str | None = None
    workspace_id: str = ""
    expires_at: str | None = None
    usage_daily: float = 0.0
    usage_weekly: float = 0.0
    usage_monthly: float = 0.0
    byok_usage: float = 0.0
    byok_usage_daily: float = 0.0
    byok_usage_weekly: float = 0.0
    byok_usage_monthly: float = 0.0
    include_byok_in_limit: bool = False
    creator_user_id: str | None = None


@dataclass
class KeyResponseWrapper(DataClassORJSONMixin):
    """Wrapper for single key response."""

    data: Key


@dataclass
class DeletedKeyResponse(DataClassORJSONMixin):
    """Response after deleting a key."""

    deleted: bool


@dataclass
class ModelResponseWrapper(DataClassORJSONMixin):
    """Wrapper for single OpenRouter model response."""

    data: Model


@dataclass
class ModelsDataWrapper(DataClassORJSONMixin):
    """Wrapper for OpenRouter model data."""

    data: list[Model]


class SupportedParameter(StrEnum):
    """Supported parameters for models."""

    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    TOP_K = "top_k"
    MAX_TOKENS = "max_tokens"
    MAX_COMPLETION_TOKENS = "max_completion_tokens"
    REASONING = "reasoning"
    REASONING_EFFORT = "reasoning_effort"
    INCLUDE_REASONING = "include_reasoning"
    STOP = "stop"
    SEED = "seed"
    RESPONSE_FORMAT = "response_format"
    STRUCTURED_OUTPUTS = "structured_outputs"
    TOOLS = "tools"
    TOOL_CHOICE = "tool_choice"
    PARALLEL_TOOL_CALLS = "parallel_tool_calls"
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    REPETITION_PENALTY = "repetition_penalty"
    MIN_P = "min_p"
    TOP_A = "top_a"
    LOGPROBS = "logprobs"
    LOGIT_BIAS = "logit_bias"
    TOP_LOGPROBS = "top_logprobs"
    WEB_SEARCH_OPTIONS = "web_search_options"
    VERBOSITY = "verbosity"


class Modality(StrEnum):
    """Supported modalities for models."""

    AUDIO = "audio"
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    EMBEDDINGS = "embeddings"
    VIDEO = "video"
    RERANK = "rerank"
    SPEECH = "speech"
    TRANSCRIPTION = "transcription"


@dataclass(kw_only=True)
class ModelArchitecture(DataClassORJSONMixin):
    """Model architecture data."""

    input_modalities: list[Modality]
    output_modalities: list[Modality]
    modality: str | None = None
    instruct_type: str | None = None
    tokenizer: str | None = None


@dataclass(kw_only=True)
class PublicPricing(DataClassORJSONMixin):
    """Model pricing data."""

    completion: str
    prompt: str
    audio: str | None = None
    audio_output: str | None = None
    image: str | None = None
    image_output: str | None = None
    image_token: str | None = None
    input_audio_cache: str | None = None
    input_cache_read: str | None = None
    input_cache_write: str | None = None
    input_cache_write_1h: str | None = None
    internal_reasoning: str | None = None
    request: str | None = None
    web_search: str | None = None
    discount: float | None = None


@dataclass(kw_only=True)
class TopProviderInfo(DataClassORJSONMixin):
    """Top provider information."""

    is_moderated: bool
    context_length: int | None = None
    max_completion_tokens: int | None = None


@dataclass(kw_only=True)
class DefaultParameters(DataClassORJSONMixin):
    """Default model parameters."""

    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    repetition_penalty: float | None = None


@dataclass(kw_only=True)
class PerRequestLimits(DataClassORJSONMixin):
    """Per-request limits."""

    completion_tokens: float
    prompt_tokens: float


@dataclass(kw_only=True)
class ModelLinks(DataClassORJSONMixin):
    """Model links."""

    details: str


@dataclass(kw_only=True)
class Model(DataClassORJSONMixin):
    """Model data."""

    id: str
    canonical_slug: str
    name: str
    context_length: int | None
    architecture: ModelArchitecture
    supported_parameters: list[SupportedParameter]
    pricing: PublicPricing
    top_provider: TopProviderInfo
    hugging_face_id: str | None = None
    description: str | None = None
    created: int | None = None
    default_parameters: DefaultParameters | None = None
    links: ModelLinks | None = None
    per_request_limits: PerRequestLimits | None = None
    supported_voices: list[str] | None = None
    expiration_date: str | None = None
    knowledge_cutoff: str | None = None

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Pre deserialize hook."""
        parameters = d.get("supported_parameters", [])
        supported = set(SupportedParameter)
        d["supported_parameters"] = [p for p in parameters if p in supported]
        for parameter in parameters:
            if parameter not in supported:
                _LOGGER.warning(
                    "Unsupported parameter: %s. Please report at https://github.com/joostlek/python-open-router/issues.",
                    parameter,
                )
        return d

    @classmethod
    def __post_deserialize__(cls, obj: Model) -> Model:
        """Post deserialize hook."""
        if obj.hugging_face_id == "":
            obj.hugging_face_id = None
        if obj.description == "":
            obj.description = None
        return obj
