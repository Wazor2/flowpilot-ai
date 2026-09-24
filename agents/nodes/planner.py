from __future__ import annotations

import json
import re
from typing import Any, Dict

from ai_provider import AllProvidersFailedError, ExecutionPlan, PlanStep as ProviderPlanStep
from agents.ai_runtime import generate_structured
from agents.state import State, PlanStep
from backend.database import SessionLocal
from backend.models import Customer
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


_PRIVATE_KEYS = {
    "name", "full_name", "customer_name", "email", "customer_email", "recipient",
    "phone", "body", "subject", "message",
}
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d().\- ]{7,}\d)(?!\w)")


def _sanitize_llm_payload(payload: dict[str, Any], customer_names: list[str] | None = None) -> dict[str, Any]:
    names = sorted((name for name in (customer_names or []) if name.strip()), key=len, reverse=True)

    def clean_text(value: str) -> str:
        value = _EMAIL_RE.sub("[REDACTED_EMAIL]", value)
        value = _PHONE_RE.sub("[REDACTED_PHONE]", value)
        for name in names:
            value = re.sub(re.escape(name), "[REDACTED_CUSTOMER]", value, flags=re.IGNORECASE)
        return value

    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: clean(item)
                for key, item in value.items()
                if key.lower() not in _PRIVATE_KEYS
            }
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, str):
            return clean_text(value)
        return value

    return clean(payload)


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
    names_db = SessionLocal()
    try:
        customer_names = [row[0] for row in names_db.query(Customer.name).all() if row[0]]
    finally:
        names_db.close()
    payload = _sanitize_llm_payload(payload, customer_names)

    try:
        plan = generate_structured(
            state.workflow_id,
            system_prompt=(
                "You are FlowPilot's planner. Produce an ExecutionPlan as JSON. "
                "Use only the registered tools supplied in the user payload. "
                "Never invent tools or actions. For invoice reminder objectives, call getOverdueInvoices first "
                "when it has not completed. Use its results to call draftInvoiceEmail for each eligible invoice "
                "that has not already been drafted. After a draft completes, plan sendEmail for that invoice_id "
                "using the locally stored draft. After a send completes, continue with other eligible invoices. "
                "The sendEmail step requires human approval; never bypass that approval. "
                "Do not create hardcoded email copy. Use completed tool results when filling later tool arguments. "
                "Include only invoice_id in a sendEmail plan; the recipient and drafted content are resolved locally."
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
