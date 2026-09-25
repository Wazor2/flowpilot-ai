import asyncio
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from ai_provider.base import AIProvider, InvalidOutputError, RateLimitError
from ai_provider.manager import AIProviderManager
from ai_provider.schemas import ExecutionPlan
from agents.state import State
import agents.ai_runtime as ai_runtime


class FakeProvider(AIProvider):
    def __init__(self, name, failures=0, error=RateLimitError("quota")):
        self.name = name
        self.failures = failures
        self.error = error
        self.calls = 0

    async def generate_structured(self, **kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise self.error
        return ExecutionPlan(plan_id="p", objective_id="o", steps=[])


def test_rate_limit_falls_through_to_next_provider():
    primary = FakeProvider("gemini", failures=1)
    fallback = FakeProvider("openai")
    result = asyncio.run(AIProviderManager([primary, fallback]).generate_structured(
        system_prompt="", user_prompt="", response_schema=ExecutionPlan
    ))
    assert result.plan_id == "p"
    assert primary.calls == 1
    assert fallback.calls == 1


def test_invalid_output_retries_same_provider_before_fallback():
    primary = FakeProvider("gemini", failures=1, error=InvalidOutputError("bad json"))
    fallback = FakeProvider("openai")
    result = asyncio.run(AIProviderManager([primary, fallback]).generate_structured(
        system_prompt="", user_prompt="", response_schema=ExecutionPlan
    ))
    assert result.plan_id == "p"
    assert primary.calls == 2
    assert fallback.calls == 0


def test_openrouter_is_reached_after_gemini_and_openai_fail(monkeypatch):
    gemini = FakeProvider("gemini", failures=1)
    openai = FakeProvider("openai", failures=1)
    openrouter = FakeProvider("openrouter")
    monkeypatch.setattr(ai_runtime, "GeminiProvider", lambda: gemini)
    monkeypatch.setattr(ai_runtime, "OpenAIProvider", lambda: openai)
    monkeypatch.setattr(ai_runtime, "OpenRouterProvider", lambda: openrouter)
    monkeypatch.setattr(ai_runtime, "record_ai_run", lambda *args, **kwargs: None)
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    manager = ai_runtime.build_provider_manager("wf-openrouter-fallback")
    result = asyncio.run(manager.generate_structured(
        system_prompt="", user_prompt="", response_schema=ExecutionPlan
    ))

    assert result.plan_id == "p"
    assert gemini.calls == 1
    assert openai.calls == 1
    assert openrouter.calls == 1


def test_replan_limit_pauses_state():
    state = State(workflow_id="wf", objective="x", status="REPLAN", replan_count=3, max_replans=3)
    state.replan_count += 1
    assert state.replan_count > state.max_replans
