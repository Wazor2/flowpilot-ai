from __future__ import annotations

import json
import os
from typing import Any, Dict

from ai_provider import AllProvidersFailedError, ExecutionPlan, PlanStep as ProviderPlanStep
from agents.ai_runtime import generate_structured
from agents.state import State, PlanStep
from backend.tools import registry


def get_tools_dictionary() -> Dict[str, Any]:
    return {
        tool_name: {
            "name": tool_name,
            "description": tool_def.description,
            "inputSchema": tool_def.inputSchema,
            "requiresApproval": tool_def.requiresApproval,
        }
        for tool_name, tool_def in registry._tools.items()
    }


def _validate_registered_tools(plan: ExecutionPlan) -> None:
    unknown = [step.tool for step in plan.steps if registry.get_tool(step.tool) is None]
    if unknown:
        raise ValueError(f"planner returned unregistered tool(s): {', '.join(unknown)}")


def planner_node(state: State) -> State:
    if state.status in ["EXECUTE", "APPROVED"] and not state.failures:
        return state

    if state.status == "REPLAN":
        state.replan_count += 1
        if state.replan_count > state.max_replans:
            state.status = "PAUSED"
            state.pause_reason = "maximum replans reached; manual intervention required"
            return state

    tools = get_tools_dictionary()
    payload = {
        "objective": state.objective,
        "completed_actions": [action.model_dump() for action in state.completed_actions],
        "failures": state.failures,
        "tools": tools,
    }

    try:
        plan = generate_structured(
            state.workflow_id,
            system_prompt=(
                "You are FlowPilot's planner. Produce an ExecutionPlan as JSON. "
                "Use only the registered tools supplied in the user payload. "
                "Never invent tools or actions."
            ),
            user_prompt=json.dumps(payload, default=str),
            response_schema=ExecutionPlan,
        )
        _validate_registered_tools(plan)
    except AllProvidersFailedError as exc:
        state.status = "PAUSED"
        state.pause_reason = f"all AI providers failed: {exc}"
        return state
    except (ValueError, TypeError) as exc:
        state.status = "PAUSED"
        state.pause_reason = f"planner output rejected: {exc}"
        return state
    except RuntimeError as exc:
        state.status = "PAUSED"
        state.pause_reason = str(exc)
        return state

    state.plan = [
        PlanStep(
            tool=step.tool,
            arguments=step.input_requirements,
            reason=step.description,
            requires_approval=step.requires_approval or bool(registry.get_tool(step.tool).requiresApproval),
        )
        for step in plan.steps
    ]
    state.current_step_index = 0
    state.failures = []
    state.status = "COMPLETED" if not state.plan else "EXECUTE"
    return state
