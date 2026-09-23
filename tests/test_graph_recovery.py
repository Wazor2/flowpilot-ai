from __future__ import annotations

import json
import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["EMAIL_MODE"] = "sandbox"

from ai_provider.schemas import ExecutionPlan, PlanStep
from agents.orchestrator import Orchestrator
from agents.state import State
import agents.nodes.planner as planner_module
from backend.database import Base, SessionLocal, engine
from backend.tool_registry import ToolDefinition, ToolResult
from backend.tools import registry


def _plan(tool: str, workflow_id: str) -> ExecutionPlan:
    return ExecutionPlan(
        plan_id=f"plan-{workflow_id}",
        objective_id=workflow_id,
        steps=[PlanStep(
            step_id="step-1",
            description=f"Run {tool}",
            tool=tool,
            input_requirements={},
            expected_output="tool result",
            requires_approval=False,
        )],
    )


def _install_test_tool(name: str, execute):
    original = registry._tools.get(name)
    registry.register_tool(ToolDefinition(
        name=name,
        description=f"Test-only tool: {name}",
        inputSchema={"type": "object", "properties": {}, "required": []},
        outputSchema={},
        requiresApproval=False,
        execute=execute,
    ))
    return original


def _restore_test_tool(name: str, original) -> None:
    if original is None:
        registry._tools.pop(name, None)
    else:
        registry._tools[name] = original


def test_graph_failure_replans_and_recovers(monkeypatch):
    Base.metadata.create_all(bind=engine)
    workflow_id = f"wf-recovery-{uuid.uuid4()}"
    calls = {"fail": 0, "recover": 0}

    def fail_once(_input, _context):
        calls["fail"] += 1
        return ToolResult(status="FAILED", error="injected failure")

    def recover(_input, _context):
        calls["recover"] += 1
        return ToolResult(status="SUCCESS", data={"recovered": True})

    original_fail = _install_test_tool("testFailOnce", fail_once)
    original_recover = _install_test_tool("testRecover", recover)

    def fake_generate(workflow_id, *, system_prompt, user_prompt, response_schema):
        payload = json.loads(user_prompt)
        return _plan("testRecover" if payload["failures"] else "testFailOnce", workflow_id)

    monkeypatch.setattr(planner_module, "generate_structured", fake_generate)
    try:
        final_state = Orchestrator().run_workflow(workflow_id, "recover after an injected tool failure")
        assert final_state.status == "COMPLETED"
        assert calls == {"fail": 1, "recover": 1}
        assert final_state.replan_count == 1
        assert len(final_state.completed_actions) == 1
    finally:
        _restore_test_tool("testFailOnce", original_fail)
        _restore_test_tool("testRecover", original_recover)


def test_graph_pauses_when_replan_limit_is_reached(monkeypatch):
    Base.metadata.create_all(bind=engine)
    workflow_id = f"wf-limit-{uuid.uuid4()}"
    attempts = {"count": 0}

    def always_fail(_input, _context):
        attempts["count"] += 1
        return ToolResult(status="FAILED", error="persistent injected failure")

    original_fail = _install_test_tool("testAlwaysFail", always_fail)

    def fake_generate(workflow_id, *, system_prompt, user_prompt, response_schema):
        return _plan("testAlwaysFail", workflow_id)

    monkeypatch.setattr(planner_module, "generate_structured", fake_generate)
    try:
        orchestrator = Orchestrator()
        state = orchestrator._run(State(
            workflow_id=workflow_id,
            objective="never recover",
            max_replans=1,
        ))
        assert state.status == "PAUSED"
        assert "maximum replans reached" in (state.pause_reason or "")
        assert state.replan_count == 2
        assert attempts["count"] == 2
    finally:
        _restore_test_tool("testAlwaysFail", original_fail)
