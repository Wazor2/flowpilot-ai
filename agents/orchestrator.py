from agents.graph import create_workflow_graph
from agents.state import State
from utils.audit_logger import AuditLogger

logger = AuditLogger()

# In-memory store for graph states
WORKFLOW_STATES = {}

class Orchestrator:
    def __init__(self):
        self.graph = create_workflow_graph()
        
    def run_workflow(self, workflow_id: str, goal: str):
        logger.log_event("Orchestrator", "Workflow Started", {"goal": goal})
        
        state = State(workflow_id=workflow_id, objective=goal)
        
        try:
            # We run the graph manually step by step so it persists if it stops
            for event in self.graph.stream(state):
                # Save state
                for k, v in event.items():
                    if isinstance(v, dict):
                        v = State(**v)
                    WORKFLOW_STATES[workflow_id] = v
            
            final_state = WORKFLOW_STATES.get(workflow_id, state)
            
            if isinstance(final_state, dict):
                final_state = State(**final_state)
            
            if final_state.status == "COMPLETED":
                logger.log_event("Orchestrator", "Workflow Completed", {"items_processed": len(final_state.completed_actions)})
            elif final_state.status == "WAITING_FOR_APPROVAL":
                logger.log_event("Orchestrator", "Workflow Paused", {"status": "WAITING_FOR_APPROVAL"})
            elif final_state.status == "FAILED":
                logger.log_event("Orchestrator", "Workflow Failed", {"failures": final_state.failures})
                
            return []
        except Exception as e:
            logger.log_event("Orchestrator", "Workflow Failed", {"error": str(e)})
            raise e
            
    def resume_workflow(self, workflow_id: str):
        if workflow_id not in WORKFLOW_STATES:
            raise ValueError("Workflow not found in memory")
            
        state = WORKFLOW_STATES[workflow_id]
        if state.status == "WAITING_FOR_APPROVAL":
            state.status = "APPROVED"
            
        logger.log_event("Orchestrator", "Workflow Resumed", {"workflow_id": workflow_id})
        
        try:
            for event in self.graph.stream(state):
                for k, v in event.items():
                    if isinstance(v, dict):
                        v = State(**v)
                    WORKFLOW_STATES[workflow_id] = v
                    
            final_state = WORKFLOW_STATES.get(workflow_id, state)
            
            if isinstance(final_state, dict):
                final_state = State(**final_state)
                
            if final_state.status == "COMPLETED":
                logger.log_event("Orchestrator", "Workflow Completed", {"items_processed": len(final_state.completed_actions)})
            elif final_state.status == "WAITING_FOR_APPROVAL":
                logger.log_event("Orchestrator", "Workflow Paused", {"status": "WAITING_FOR_APPROVAL"})
            elif final_state.status == "FAILED":
                logger.log_event("Orchestrator", "Workflow Failed", {"failures": final_state.failures})
        except Exception as e:
            logger.log_event("Orchestrator", "Workflow Failed", {"error": str(e)})
            raise e
