from __future__ import annotations

import json
import os
import asyncio
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from .base import (
    AIProvider,
    InvalidOutputError,
    ProviderUnavailableError,
    RateLimitError,
)

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        import google.generativeai as genai  # local import: optional dependency

        self._genai = genai
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        genai.configure(api_key=api_key)
        self.model_name = model or os.environ.get(
            "AI_MODEL_GEMINI", "gemini-1.5-flash-latest"
        )
        self._model = genai.GenerativeModel(self.model_name)

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
    ) -> T:
        from google.api_core import exceptions as g_exceptions

        prompt = (
            f"{system_prompt}\n\n"
            f"Respond with ONLY valid JSON matching this schema, no prose, "
            f"no markdown fences:\n{response_schema.model_json_schema()}\n\n"
            f"{user_prompt}"
        )

        try:
            result = await asyncio.to_thread(
                self._model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            )
        except g_exceptions.ResourceExhausted as exc:
            raise RateLimitError(f"gemini quota exhausted: {exc}") from exc
        except g_exceptions.ServiceUnavailable as exc:
            raise ProviderUnavailableError(f"gemini unavailable: {exc}") from exc
        except g_exceptions.DeadlineExceeded as exc:
            raise ProviderUnavailableError(f"gemini timeout: {exc}") from exc
        except Exception as exc:
            if getattr(exc, "code", None) == 429 or "429" in str(exc) or "resource exhausted" in str(exc).lower():
                raise RateLimitError(f"gemini rate limit: {exc}") from exc
            raise ProviderUnavailableError(f"gemini request failed: {exc}") from exc

        raw_text = result.text
        try:
            return response_schema.model_validate(json.loads(raw_text))
        except (AttributeError, json.JSONDecodeError, ValidationError) as exc:
            raise InvalidOutputError(f"gemini returned invalid output: {exc}") from exc
