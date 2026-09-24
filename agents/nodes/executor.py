from __future__ import annotations

import uuid
import json

from agents.state import State, ToolExecutionResult
from backend.database import SessionLocal
from backend.models import Invoice, Workflow
from backend.tool_registry import ToolContext
from backend.tools import registry
from utils.audit_logger import AuditLogger

logger = AuditLogger()


def _action_id_for_step(state: State, step) -> str:
    if step.tool == "sendEmail":
        invoice_id = step.arguments.get("invoice_id")
        identity = f"invoice:{invoice_id}" if invoice_id else json.dumps(step.arguments, sort_keys=True, default=str)
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"flowpilot:{state.workflow_id}:sendEmail:{identity}"))
    return str(uuid.uuid4())


def _recheck_invoice_before_send(db, state: State, step, action_id: str) -> bool:
    """Return true when a send must be cancelled because its invoice is no longer overdue."""
    invoice_id = step.arguments.get("invoice_id")
    if step.tool != "sendEmail" or not invoice_id:
        return False

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    status = invoice.status.upper() if invoice and invoice.status else "MISSING"
    if invoice and status == "OVERDUE":
        return False

    resolved = status in {"PAID", "CANCELLED", "VOID", "RESOLVED"}
    case_status = "RESOLVED" if resolved else "ON_HOLD"
    reason = (
        f"Invoice {invoice_id} is now {status}; the approved reminder was cancelled before sending."
        if invoice else f"Invoice {invoice_id} no longer exists; the approved reminder was cancelled."
    )
    workflow = db.query(Workflow).filter(Workflow.id == state.workflow_id).first()
    if workflow:
        workflow.status = case_status
        db.commit()

    logger.log_event(
        "ExecutorAgent",
        "PRE_EXECUTION_SEND_CANCELLED",
        {"invoice_id": invoice_id, "invoice_status": status, "action_id": action_id},
        workflow_id=state.workflow_id,
        tool=step.tool,
        status=case_status,
        approval_state="CANCELLED",
        reason=reason,
    )
    state.completed_actions.append(ToolExecutionResult(
        tool_name=step.tool,
        arguments={"invoice_id": invoice_id},
        result={"cancelled": True, "invoice_status": status, "reason": reason},
        status="CANCELLED",
    ))
    if resolved:
        state.status = "COMPLETED"
    else:
        state.status = "PAUSED"
        state.pause_reason = reason
    return True


def executor_node(state: State) -> State:
    if state.current_step_index >= len(state.plan):
        state.status = "REPLAN" if state.failures else "COMPLETED"
        return state

    step = state.plan[state.current_step_index]
    if step.requires_approval and state.status != "APPROVED":
        logger.log_event(
            "ExecutorAgent", "Approval Required", {"tool": step.tool, "reason": step.reason},
            workflow_id=state.workflow_id, tool=step.tool, status="WAITING_FOR_APPROVAL",
            approval_state="PENDING",
        )
        state.status = "WAITING_FOR_APPROVAL"
        return state

    action_key = f"{state.current_step_index}:{step.tool}"
    attempts = state.action_attempts.get(action_key, 0) + 1
    state.action_attempts[action_key] = attempts
    if attempts > state.max_execution_attempts_per_action:
        state.status = "PAUSED"
        state.pause_reason = f"maximum execution attempts reached for {step.tool}; manual intervention required"
        logger.log_event(
            "ExecutorAgent", "Action Attempt Limit Reached", {"tool": step.tool, "attempts": attempts},
            workflow_id=state.workflow_id, tool=step.tool, status="PAUSED", reason=state.pause_reason,
        )
        return state

    db = SessionLocal()
    try:
        action_id = _action_id_for_step(state, step)
        if _recheck_invoice_before_send(db, state, step, action_id):
            return state

        logger.log_event(
            "ExecutorAgent", "Executing Task", {"tool": step.tool, "arguments": step.arguments},
            workflow_id=state.workflow_id, tool=step.tool, status="RUNNING",
        )
        ctx = ToolContext(
            workflow_id=state.workflow_id,
            step_id=f"step-{state.current_step_index}",
            action_id=action_id,
            db=db,
        )
        result = registry.execute_tool(step.tool, step.arguments, ctx)
        exec_result = ToolExecutionResult(
            tool_name=step.tool,
            arguments=step.arguments,
            result=result.data if result.data else {"error": result.error},
            status=result.status,
        )
        if result.status == "FAILED":
            state.failures.append({"tool": step.tool, "arguments": step.arguments, "error": result.error})
            state.status = "REPLAN"
            logger.log_event(
                "ExecutorAgent", "Task Failed", {"tool": step.tool, "error": result.error},
                workflow_id=state.workflow_id, tool=step.tool, status="FAILED", reason=result.error,
            )
        else:
            state.completed_actions.append(exec_result)
            state.current_step_index += 1
            state.status = "REPLAN" if step.tool in {"getOverdueInvoices", "draftInvoiceEmail", "sendEmail"} else "EXECUTE"
            logger.log_event(
                "ExecutorAgent", "Task Success", {"tool": step.tool, "result": result.data},
                workflow_id=state.workflow_id, tool=step.tool, status="SUCCESS",
            )
    except Exception as exc:
        state.failures.append({"tool": step.tool, "error": str(exc)})
        state.status = "REPLAN"
        logger.log_event(
            "ExecutorAgent", "Task Exception", {"tool": step.tool, "error": str(exc)},
            workflow_id=state.workflow_id, tool=step.tool, status="FAILED", reason=str(exc),
        )
    finally:
        db.close()
    return state
