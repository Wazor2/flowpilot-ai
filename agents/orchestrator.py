from agents.graph import create_workflow_graph
from agents.state import State
from utils.audit_logger import AuditLogger

logger = AuditLogger()
WORKFLOW_STATES: dict[str, State] = {}


class Orchestrator:
    def __init__(self):
        self.graph = create_workflow_graph()

    def _run(self, state: State) -> State:
        for event in self.graph.stream(state):
            for value in event.values():
                WORKFLOW_STATES[state.workflow_id] = value if isinstance(value, State) else State(**value)
        return WORKFLOW_STATES.get(state.workflow_id, state)

    def run_workflow(self, workflow_id: str, goal: str):
        logger.log_event("Orchestrator", "Workflow Started", {"goal": goal}, workflow_id=workflow_id, status="STARTED")
        state = self._run(State(workflow_id=workflow_id, objective=goal))
        if state.status == "COMPLETED":
            logger.log_event("Orchestrator", "Workflow Completed", {"items_processed": len(state.completed_actions)}, workflow_id=workflow_id, status="COMPLETED")
        elif state.status in {"WAITING_FOR_APPROVAL", "PAUSED"}:
            logger.log_event("Orchestrator", "Workflow Paused", {"reason": state.pause_reason}, workflow_id=workflow_id, status=state.status, reason=state.pause_reason)
        return state

    def resume_workflow(self, workflow_id: str):
        if workflow_id not in WORKFLOW_STATES:
            raise ValueError("Workflow not found in memory")
        state = WORKFLOW_STATES[workflow_id]
        if state.status == "WAITING_FOR_APPROVAL":
            state.status = "APPROVED"
        return self._run(state)
