"""Run the requested workflow and wait for explicit approval before sendEmail."""

import uuid

from agents.orchestrator import Orchestrator
from backend.database import SessionLocal
from backend.models import Workflow
from backend.tools.email_tool import get_email_mode


def main() -> None:
    if get_email_mode() != "live":
        raise RuntimeError("EMAIL_MODE is not live; refusing workflow run")

    workflow_id = str(uuid.uuid4())
    objective = "review overdue invoices and send a reminder"
    db = SessionLocal()
    try:
        db.add(Workflow(id=workflow_id, objective=objective, mode="AUTONOMOUS"))
        db.commit()
    finally:
        db.close()

    orchestrator = Orchestrator()
    state = orchestrator.run_workflow(workflow_id=workflow_id, goal=objective)
    print(f"WORKFLOW_ID={workflow_id}", flush=True)
    sequence = [action.tool_name for action in state.completed_actions]
    if state.status == "WAITING_FOR_APPROVAL" and state.current_step_index < len(state.plan):
        sequence.append(state.plan[state.current_step_index].tool)
    print("TOOL_SEQUENCE=" + " -> ".join(sequence), flush=True)

    for action in state.completed_actions:
        if action.tool_name == "draftInvoiceEmail":
            print("DRAFT_SUBJECT=" + str(action.result.get("subject", "")), flush=True)
            print("DRAFT_BODY_BEGIN", flush=True)
            print(str(action.result.get("body", "")), flush=True)
            print("DRAFT_BODY_END", flush=True)

    print(f"STATUS={state.status}", flush=True)
    if state.status != "WAITING_FOR_APPROVAL":
        return

    print("Paused before sendEmail. To continue, reply exactly approved in chat.", flush=True)
    approval = input()
    if approval.strip().lower() != "approved":
        print("No approval received; email was not sent.", flush=True)
        return

    resumed = orchestrator.resume_workflow(workflow_id)
    print(f"RESUMED_STATUS={resumed.status}", flush=True)
    for action in resumed.completed_actions:
        if action.tool_name == "sendEmail":
            print("SEND_RESULT=" + str(action.result), flush=True)


if __name__ == "__main__":
    main()
