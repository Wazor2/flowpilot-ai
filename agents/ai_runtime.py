from __future__ import annotations

import asyncio
import os
import threading
import uuid
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

from ai_provider import AIProviderManager, GeminiProvider, OpenAIProvider
from backend.database import SessionLocal
from backend.models import AiRun, AuditEvent

T = TypeVar("T", bound=BaseModel)


def record_ai_run(
    workflow_id: str,
    provider_name: str,
    attempt: int,
    success: bool,
    error: Optional[str],
) -> None:
    """Persist every provider attempt in the authoritative database."""
    db = SessionLocal()
    try:
        status = "SUCCESS" if success else "FAILED"
        db.add(AiRun(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            provider=provider_name,
            attempt=attempt,
            status=status,
            error=error,
        ))
        db.add(AuditEvent(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            event_type="AI_PROVIDER_ATTEMPT",
            actor="AIProviderManager",
            tool=provider_name,
            status=status,
            input_summary=f"provider={provider_name}; attempt={attempt}",
            result_summary="structured output validated" if success else None,
            reason=error,
            summary=error or "structured output validated",
            metadata_json={"provider": provider_name, "attempt": attempt},
        ))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def build_provider_manager(workflow_id: str) -> AIProviderManager:
    providers = []
    if os.getenv("GEMINI_API_KEY"):
        providers.append(GeminiProvider())
    if os.getenv("OPENAI_API_KEY"):
        providers.append(OpenAIProvider())
    if not providers:
        raise RuntimeError("No AI provider configured; set GEMINI_API_KEY and/or OPENAI_API_KEY")
    return AIProviderManager(
        providers=providers,
        max_validation_retries=1,
        audit_hook=lambda provider, attempt, success, error: record_ai_run(
            workflow_id, provider, attempt, success, error
        ),
    )


def run_async(coro: Any) -> Any:
    """Bridge async SDK calls into LangGraph's synchronous node API."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: list[Any] = []
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            result.append(asyncio.run(coro))
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()
    if errors:
        raise errors[0]
    return result[0]


def generate_structured(
    workflow_id: str,
    *,
    system_prompt: str,
    user_prompt: str,
    response_schema: Type[T],
) -> T:
    manager = build_provider_manager(workflow_id)
    return run_async(manager.generate_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=response_schema,
    ))
