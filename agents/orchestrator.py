from agents.agent_roles import PlannerAgent, ExecutorAgent, SafeguardVerifierAgent
from utils.audit_logger import AuditLogger

logger = AuditLogger()

class Orchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = SafeguardVerifierAgent()
        
    def run_workflow(self, goal="Identify and recover all overdue invoices"):
        logger.log_event("Orchestrator", "Workflow Started", {"goal": goal})
        
        # Step 1: Planning
        plan = self.planner.plan_recovery(goal)
        
        # Step 2: Execution with dynamic fallback loop
        execution_results = self.executor.execute_plan(plan)
        
        # Step 3: Verification
        final_results = self.verifier.verify_results(execution_results)
        
        logger.log_event("Orchestrator", "Workflow Completed", {"items_processed": len(final_results)})
        return final_results
