from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import sys
import os
import json
import secrets
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import Request
from fastapi.responses import RedirectResponse

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
GOOGLE_STATE_COOKIE = "flowpilot_google_oauth_state"
GOOGLE_VERIFIER_COOKIE = "flowpilot_google_oauth_code_verifier"
GMAIL_TOKEN_PATH = Path(__file__).resolve().parents[1] / ".gmail_token.json"


def _google_oauth_config() -> tuple[dict[str, Any], str]:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }, redirect_uri


@app.get("/auth/google/login")
def google_oauth_login(request: Request):
    from google_auth_oauthlib.flow import Flow

    client_config, redirect_uri = _google_oauth_config()
    state = secrets.token_urlsafe(32)
    flow = Flow.from_client_config(
        client_config,
        scopes=[GMAIL_SEND_SCOPE],
        state=state,
        redirect_uri=redirect_uri,
    )
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    response = RedirectResponse(authorization_url, status_code=302)
    response.set_cookie(
        GOOGLE_STATE_COOKIE,
        state,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=600,
        path="/auth/google",
    )
    response.set_cookie(
        GOOGLE_VERIFIER_COOKIE,
        flow.code_verifier,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=600,
        path="/auth/google",
    )
    return response


@app.get("/auth/google/callback")
def google_oauth_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    from google_auth_oauthlib.flow import Flow

    if error:
        raise HTTPException(status_code=400, detail="Google authorization was not completed")
    cookie_state = request.cookies.get(GOOGLE_STATE_COOKIE, "")
    if not state or not cookie_state or not secrets.compare_digest(state, cookie_state):
        raise HTTPException(status_code=400, detail="Invalid or expired Google OAuth state")
    if not code:
        raise HTTPException(status_code=400, detail="Google authorization code is missing")
    code_verifier = request.cookies.get(GOOGLE_VERIFIER_COOKIE, "")
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Google OAuth code verifier is missing or expired")

    client_config, redirect_uri = _google_oauth_config()
    flow = Flow.from_client_config(
        client_config,
        scopes=[GMAIL_SEND_SCOPE],
        state=state,
        redirect_uri=redirect_uri,
    )
    flow.code_verifier = code_verifier
    try:
        flow.fetch_token(code=code)
    except Exception as exc:
        print(f"Google OAuth token exchange failed ({type(exc).__name__}): {exc}")
        raise HTTPException(status_code=400, detail="Google authorization code exchange failed") from exc

    refresh_token = flow.credentials.refresh_token
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Google did not issue a refresh token; revisit /auth/google/login and approve offline access",
        )

    token_path = GMAIL_TOKEN_PATH
    token_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=token_path.parent, prefix=".gmail-token-", suffix=".tmp", delete=False
        ) as token_file:
            temp_path = Path(token_file.name)
            os.chmod(temp_path, 0o600)
            json.dump({"refresh_token": refresh_token}, token_file)
        os.replace(temp_path, token_path)
        try:
            os.chmod(token_path, 0o600)
        except OSError:
            pass
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)

    response = RedirectResponse("http://localhost:8000/docs", status_code=303)
    response.delete_cookie(GOOGLE_STATE_COOKIE, path="/auth/google")
    response.delete_cookie(GOOGLE_VERIFIER_COOKIE, path="/auth/google")
    return response

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

@app.get("/api/workflows")
def list_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).order_by(Workflow.created_at.desc()).all()

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

@app.get("/api/workflows/{id}/approvals")
def get_workflow_approvals(id: str, db: Session = Depends(get_db)):
    approvals = db.query(Approval).filter(Approval.workflow_id == id).order_by(Approval.requested_at.desc()).all()
    drafts = db.query(ToolExecution).filter(
        ToolExecution.workflow_id == id,
        ToolExecution.tool_name == "draftInvoiceEmail",
        ToolExecution.status == "SUCCESS",
    ).order_by(ToolExecution.started_at.desc()).all()
    latest_drafts = [row.output for row in drafts if row.output]
    return [
        {
            "id": approval.id,
            "workflow_id": approval.workflow_id,
            "action": approval.action,
            "reason": approval.reason,
            "requested_at": approval.requested_at,
            "requested_by": approval.requested_by,
            "status": approval.status,
            "draft": next(
                (draft for draft in latest_drafts if draft.get("invoice_id") and approval.action in {"sendEmail", "draftInvoiceEmail"}),
                latest_drafts[0] if latest_drafts else None,
            ),
        }
        for approval in approvals
    ]

@app.get("/api/approvals")
def list_pending_approvals(db: Session = Depends(get_db)):
    return [
        approval
        for workflow in db.query(Workflow).filter(Workflow.status == "WAITING_FOR_APPROVAL").all()
        for approval in get_workflow_approvals(workflow.id, db)
        if approval["status"] == "PENDING"
    ]

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

@app.post("/api/customers")
def create_customer(payload: Dict[str, Any], db: Session = Depends(get_db)):
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip()
    if not name or not email:
        raise HTTPException(status_code=400, detail="Customer name and email are required")
    customer = Customer(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        phone=payload.get("phone"),
        status=payload.get("status", "ACTIVE"),
        risk_level=payload.get("risk_level", "LOW"),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@app.get("/api/customers")
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@app.post("/api/invoices")
def create_invoice(payload: Dict[str, Any], db: Session = Depends(get_db)):
    customer_id = str(payload.get("customer_id", "")).strip()
    if not customer_id or not db.query(Customer).filter(Customer.id == customer_id).first():
        raise HTTPException(status_code=400, detail="A valid customer_id is required")
    try:
        due_date = datetime.fromisoformat(str(payload["due_date"]).replace("Z", "+00:00"))
        amount = float(payload["amount"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="amount and ISO due_date are required") from exc
    invoice = Invoice(
        id=str(uuid.uuid4()),
        invoice_number=payload.get("invoice_number") or f"INV-{uuid.uuid4().hex[:8].upper()}",
        customer_id=customer_id,
        amount=amount,
        due_date=due_date,
        status=payload.get("status", "PENDING"),
        days_overdue=int(payload.get("days_overdue", 0)),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice
