from __future__ import annotations

import json
import os
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from .base import (
    AIProvider,
    InvalidOutputError,
    ProviderUnavailableError,
    RateLimitError,
)

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        from openai import AsyncOpenAI  # local import: optional dependency

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self._client = AsyncOpenAI(api_key=api_key)
        self.model_name = model or os.environ.get("AI_MODEL_OPENAI", "gpt-4o-mini")

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
    ) -> T:
        import openai

        try:
            response = await self._client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"{system_prompt}\n\nRespond with ONLY valid JSON "
                            f"matching this schema:\n"
                            f"{response_schema.model_json_schema()}"
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
            )
        except openai.RateLimitError as exc:
            raise RateLimitError(f"openai quota/rate limit: {exc}") from exc
        except (openai.APITimeoutError, openai.APIConnectionError, openai.InternalServerError) as exc:
            raise ProviderUnavailableError(f"openai unavailable: {exc}") from exc
        except Exception as exc:
            if getattr(exc, "status_code", None) == 429 or "429" in str(exc):
                raise RateLimitError(f"openai rate limit: {exc}") from exc
            raise ProviderUnavailableError(f"openai request failed: {exc}") from exc

        raw_text = response.choices[0].message.content or ""
        try:
            data = json.loads(raw_text)
            return response_schema.model_validate(data)
        except (IndexError, AttributeError, json.JSONDecodeError, ValidationError) as exc:
            raise InvalidOutputError(f"openai returned invalid output: {exc}") from exc
