"""
Provider-agnostic LLM interface for FlowPilot.

Every concrete provider (Gemini, OpenAI, ...) implements this interface.
Callers (the Planner node, Decision Engine, Replanner) never talk to a
provider SDK directly -- they only talk to AIProviderManager, which talks
to AIProvider implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ProviderError(Exception):
    """Base class for all provider-level failures."""


class RateLimitError(ProviderError):
    """Raised when a provider is out of quota / rate-limited (e.g. HTTP 429).

    This is the specific error that must trigger a fallback to the next
    provider in AIProviderManager, rather than failing the whole workflow.
    """


class ProviderUnavailableError(ProviderError):
    """Raised on network/timeout/5xx errors -- provider is temporarily down."""


class InvalidOutputError(ProviderError):
    """Raised when the provider's response cannot be parsed into the
    requested schema, even after the provider's own retry attempts."""


class AIProvider(ABC):
    """Common interface every LLM provider must implement."""

    name: str = "base"

    @abstractmethod
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
    ) -> T:
        """Call the model and return output validated against response_schema.

        Implementations must:
          - request JSON/structured output from the underlying model
          - parse the raw response and validate it with response_schema
          - raise InvalidOutputError if validation fails
          - raise RateLimitError on quota/429 errors
          - raise ProviderUnavailableError on timeouts / 5xx / network errors
          - never raise a raw SDK exception -- always translate it into one
            of the errors above so AIProviderManager can react correctly
        """
        raise NotImplementedError
