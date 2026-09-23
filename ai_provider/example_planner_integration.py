"""
Example: how agents/nodes/planner.py plugs into AIProviderManager instead
of calling Gemini directly. Adapt the State type / imports to match your
actual agents/state.py.
"""

from __future__ import annotations

import os

from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .manager import AIProviderManager, AllProvidersFailedError
from .schemas import ExecutionPlan


def build_manager(record_ai_run) -> AIProviderManager:
    """
    record_ai_run(provider_name, attempt, success, error) should write a row
    into the ai_runs table / emit an audit_event -- keeps this module
    decoupled from your SQLAlchemy models.
    """
    providers = [
        GeminiProvider(api_key=os.environ["GEMINI_API_KEY"]),
    ]
    if os.environ.get("OPENAI_API_KEY"):
        providers.append(OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"]))
    else:
        # No fallback configured -- log this loudly at startup, don't fail
        # silently later when Gemini's quota runs out mid-demo.
        import logging

        logging.getLogger("flowpilot.ai_provider").warning(
            "OPENAI_API_KEY not set -- no fallback provider configured, "
            "Gemini rate limits will hard-fail the workflow"
        )

    return AIProviderManager(providers=providers, audit_hook=record_ai_run)


async def planner_node(state, manager: AIProviderManager) -> dict:
    """Drop-in replacement body for agents/nodes/planner.py's planner function."""
    try:
        plan = await manager.generate_structured(
            system_prompt=(
                "You are FlowPilot's planner. Given a business objective and "
                "the list of available tools below, produce a structured "
                "ExecutionPlan. Only use tools from the provided list."
            ),
            user_prompt=(
                f"Objective: {state.objective}\n"
                f"Available tools: {state.available_tools}\n"
                f"Prior failures (if any): {state.failures}"
            ),
            response_schema=ExecutionPlan,
        )
    except AllProvidersFailedError as exc:
        # Match section 22/35 of the spec: pause, don't crash, don't guess.
        return {
            "status": "PAUSED",
            "pause_reason": f"planner unable to reach any AI provider: {exc}",
        }

    return {"status": "PLANNED", "plan": plan}
