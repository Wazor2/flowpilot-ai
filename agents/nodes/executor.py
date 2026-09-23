from __future__ import annotations

import uuid

from agents.state import State, ToolExecutionResult
from backend.database import SessionLocal
from backend.tool_registry import ToolContext
from backend.tools import registry
from utils.audit_logger import AuditLogger

logger = AuditLogger()


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

    logger.log_event(
        "ExecutorAgent", "Executing Task", {"tool": step.tool, "arguments": step.arguments},
        workflow_id=state.workflow_id, tool=step.tool, status="RUNNING",
    )
    db = SessionLocal()
    try:
        ctx = ToolContext(
            workflow_id=state.workflow_id,
            step_id=f"step-{state.current_step_index}",
            action_id=str(uuid.uuid4()),
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
            state.status = "EXECUTE"
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
