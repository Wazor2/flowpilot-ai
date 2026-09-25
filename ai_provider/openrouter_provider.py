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
OPENROUTER_FREE_MODEL = "google/gemini-2.0-flash-exp:free"


class OpenRouterProvider(AIProvider):
    name = "openrouter"

    def __init__(self, api_key: str | None = None, model: str = OPENROUTER_FREE_MODEL):
        from openai import AsyncOpenAI

        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model_name = model

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
                            f"matching this schema:\n{response_schema.model_json_schema()}"
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
            )
        except openai.RateLimitError as exc:
            raise RateLimitError(f"openrouter quota/rate limit: {exc}") from exc
        except (
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.InternalServerError,
        ) as exc:
            raise ProviderUnavailableError(f"openrouter unavailable: {exc}") from exc
        except Exception as exc:
            status_code = getattr(exc, "status_code", None)
            if status_code == 429 or "429" in str(exc):
                raise RateLimitError(f"openrouter rate limit: {exc}") from exc
            raise ProviderUnavailableError(f"openrouter request failed: {exc}") from exc

        try:
            raw_text = response.choices[0].message.content or ""
            return response_schema.model_validate(json.loads(raw_text))
        except (IndexError, AttributeError, json.JSONDecodeError, ValidationError) as exc:
            raise InvalidOutputError(f"openrouter returned invalid output: {exc}") from exc
