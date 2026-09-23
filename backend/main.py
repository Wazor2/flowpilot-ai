from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import sys
import os

# Add root directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.orchestrator import Orchestrator

from .database import get_db, Base, engine
from .models import Workflow, AuditEvent, Approval, Invoice, Customer, Payment, Communication, ToolExecution, Replan
from .tool_registry import ToolContext
from .tools import registry

# For testing, we create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlowPilot Backend API")

def run_orchestrator(workflow_id: str):
    from backend.database import SessionLocal
    from backend.models import Workflow
    try:
        orchestrator = Orchestrator()
        db = SessionLocal()
        try:
            wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            objective = wf.objective if wf else "Unknown"
        finally:
            db.close()
            
        state = orchestrator.run_workflow(workflow_id=workflow_id, goal=objective)
        db = SessionLocal()
        try:
            wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if wf:
                wf.status = state.status
                wf.current_plan = [step.model_dump() for step in state.plan]
                wf.current_step = str(state.current_step_index)
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Workflow execution failed: {e}")
        db = SessionLocal()
        try:
            wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if wf:
                wf.status = "FAILED"
                db.commit()
        finally:
            db.close()

@app.post("/api/workflows")
def create_workflow(payload: Dict[str, Any], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    wf = Workflow(id=str(uuid.uuid4()), objective=payload.get("objective", "Unknown"), mode=payload.get("mode", "AUTONOMOUS"))
    db.add(wf)
    db.commit()
    db.refresh(wf)
    
    background_tasks.add_task(run_orchestrator, wf.id)
    
    return {"id": wf.id, "status": wf.status}

@app.get("/api/workflows/{id}")
def get_workflow(id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf

@app.get("/api/workflows/{id}/events")
def get_workflow_events(id: str, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).filter(AuditEvent.workflow_id == id).all()
    return events

@app.post("/api/workflows/{id}/approve")
def approve_action(id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    approval_id = payload.get("approval_id")
    approval = db.query(Approval).filter(Approval.id == approval_id, Approval.workflow_id == id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval.status = "APPROVED"
    approval.approved_by = payload.get("actor", "SYSTEM")
    db.commit()
    
    # Resume the orchestrator
    try:
        orchestrator = Orchestrator()
        orchestrator.resume_workflow(workflow_id=id)
    except Exception as e:
        print(f"Failed to resume workflow: {e}")
        
    return {"status": "APPROVED"}

@app.post("/api/workflows/{id}/reject")
def reject_action(id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    approval_id = payload.get("approval_id")
    approval = db.query(Approval).filter(Approval.id == approval_id, Approval.workflow_id == id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval.status = "REJECTED"
    db.commit()
    return {"status": "REJECTED"}

@app.post("/api/workflows/{id}/replan")
def trigger_replan(id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    replan = Replan(
        id=str(uuid.uuid4()),
        workflow_id=id,
        trigger=payload.get("trigger", "FAILURE"),
        failure_context=payload.get("failure_context"),
        new_plan=payload.get("new_plan")
    )
    db.add(replan)
    db.commit()
    return {"status": "REPLAN_LOGGED", "replan_id": replan.id}

@app.post("/api/workflows/{id}/execute-tool")
def execute_tool(id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    tool_name = payload.get("tool_name")
    input_data = payload.get("input_data", {})
    step_id = payload.get("step_id", "step-0")
    action_id = payload.get("action_id", str(uuid.uuid4()))
    
    ctx = ToolContext(workflow_id=id, step_id=step_id, action_id=action_id, db=db)
    result = registry.execute_tool(tool_name, input_data, ctx)
    return result.model_dump()

@app.get("/api/invoices")
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()

@app.get("/api/customers")
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()
