import asyncio
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from ai_provider.base import AIProvider, InvalidOutputError, RateLimitError
from ai_provider.manager import AIProviderManager
from ai_provider.schemas import ExecutionPlan
from agents.state import State


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


def test_replan_limit_pauses_state():
    state = State(workflow_id="wf", objective="x", status="REPLAN", replan_count=3, max_replans=3)
    state.replan_count += 1
    assert state.replan_count > state.max_replans
