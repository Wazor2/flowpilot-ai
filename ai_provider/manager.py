from __future__ import annotations

import logging
from typing import Callable, Optional, Sequence, Type, TypeVar

from pydantic import BaseModel

from .base import AIProvider, InvalidOutputError, ProviderError, RateLimitError, ProviderUnavailableError

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger("flowpilot.ai_provider")

# Called after every attempt (success or failure) so the caller can write an
# ai_runs row / audit_event without the manager needing to know about
# PostgreSQL. Signature: (provider_name, attempt_number, success, error)
AuditHook = Callable[[str, int, bool, Optional[str]], None]


class AllProvidersFailedError(ProviderError):
    """Raised when every configured provider failed for this call."""


class AIProviderManager:
    """
    Tries providers in order (e.g. [GeminiProvider(), OpenAIProvider()]).

    - RateLimitError / ProviderUnavailableError on a provider -> immediately
      fall through to the next provider (this is the quota-exhaustion fix).
    - InvalidOutputError -> retry the SAME provider up to
      `max_validation_retries` times before falling through, since malformed
      JSON is often a one-off, not a real outage.
    - If every provider is exhausted, raises AllProvidersFailedError so the
      caller (e.g. the LangGraph node) can pause the workflow instead of
      executing anything.
    """

    def __init__(
        self,
        providers: Sequence[AIProvider],
        max_validation_retries: int = 1,
        audit_hook: Optional[AuditHook] = None,
    ):
        if not providers:
            raise ValueError("AIProviderManager requires at least one provider")
        self._providers = list(providers)
        self._max_validation_retries = max_validation_retries
        self._audit_hook = audit_hook

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
    ) -> T:
        attempt = 0
        last_error: Optional[Exception] = None

        for provider in self._providers:
            validation_attempts_left = self._max_validation_retries + 1

            while validation_attempts_left > 0:
                attempt += 1
                validation_attempts_left -= 1
                try:
                    result = await provider.generate_structured(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        response_schema=response_schema,
                    )
                    self._audit(provider.name, attempt, True, None)
                    return result

                except InvalidOutputError as exc:
                    last_error = exc
                    self._audit(provider.name, attempt, False, str(exc))
                    logger.warning(
                        "provider=%s invalid output (retries left=%d): %s",
                        provider.name,
                        validation_attempts_left,
                        exc,
                    )
                    continue  # retry same provider

                except (RateLimitError, ProviderUnavailableError) as exc:
                    last_error = exc
                    self._audit(provider.name, attempt, False, str(exc))
                    logger.warning(
                        "provider=%s unavailable, falling back: %s",
                        provider.name,
                        exc,
                    )
                    break  # stop retrying this provider, try next one

        raise AllProvidersFailedError(
            f"all {len(self._providers)} provider(s) failed; last error: {last_error}"
        ) from last_error

    def _audit(self, provider_name: str, attempt: int, success: bool, error: Optional[str]) -> None:
        if self._audit_hook is not None:
            self._audit_hook(provider_name, attempt, success, error)
