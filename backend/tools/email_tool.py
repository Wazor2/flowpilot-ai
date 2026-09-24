import os
import json
import uuid
import base64
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Any

from pydantic import BaseModel, Field
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from agents.ai_runtime import generate_structured
from ..models import Communication, Customer, Invoice, ToolExecution
from ..tool_registry import ToolResult, ToolContext


class InvoiceEmailDraft(BaseModel):
    subject: str = Field(min_length=1, max_length=180)
    body: str = Field(min_length=1)


GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
GMAIL_TOKEN_PATH = Path(__file__).resolve().parents[2] / ".gmail_token.json"


def _send_via_gmail_api(recipient: str, subject: str, body: str) -> dict[str, Any]:
    if not GMAIL_TOKEN_PATH.exists():
        raise FileNotFoundError("Gmail refresh token is missing")
    try:
        token_data = json.loads(GMAIL_TOKEN_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FileNotFoundError("Gmail refresh token is unavailable") from exc
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise FileNotFoundError("Gmail refresh token is missing")

    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError("Google OAuth client credentials are not configured")

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[GMAIL_SEND_SCOPE],
    )
    credentials.refresh(Request())

    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii").rstrip("=")
    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    return service.users().messages().send(
        userId="me",
        body={"raw": raw_message},
    ).execute()

def get_email_mode() -> str:
    return os.getenv("EMAIL_MODE", "sandbox").lower()


def draft_invoice_email_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    invoice_id = input_data.get("invoice_id")
    if not invoice_id:
        return ToolResult(status="FAILED", error="Missing invoice_id")

    invoice = context.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return ToolResult(status="FAILED", error="Invoice not found")
    customer = context.db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    if not customer:
        return ToolResult(status="FAILED", error="Invoice customer not found")
    if not customer.email:
        return ToolResult(status="FAILED", error="Customer has no email address")

    facts = {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number or invoice.id,
        "amount": invoice.amount,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "status": invoice.status,
        "days_overdue": invoice.days_overdue,
    }
    try:
        draft = generate_structured(
            context.workflow_id,
            system_prompt=(
                "Write a concise, courteous invoice reminder email. Use only the supplied facts and do not use a person's name. "
                "Do not claim that payment was received, threaten consequences, or invent a payment link. "
                "Ask the recipient to contact us if they have already paid or need help. Return a clear subject and body."
            ),
            user_prompt=str(facts),
            response_schema=InvoiceEmailDraft,
        )
    except Exception as exc:
        return ToolResult(status="FAILED", error=f"Could not draft invoice email: {exc}")

    return ToolResult(status="SUCCESS", data={
        "invoice_id": invoice.id,
        "customer_id": customer.id,
        "recipient": customer.email,
        "subject": draft.subject,
        "body": draft.body,
    })

def prepare_email_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    subject = input_data.get("subject", "No Subject")
    body = input_data.get("body", "")
    recipient = input_data.get("recipient")
    
    if not recipient:
        return ToolResult(status="FAILED", error="Missing recipient")
        
    return ToolResult(status="SUCCESS", data={"subject": subject, "body": body, "recipient": recipient, "prepared": True})

def send_email_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    recipient = input_data.get("recipient")
    subject = input_data.get("subject")
    body = input_data.get("body")
    invoice_id = input_data.get("invoice_id")

    if invoice_id:
        invoice = context.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return ToolResult(status="FAILED", error="Invoice not found at send time")
        customer = context.db.query(Customer).filter(Customer.id == invoice.customer_id).first()
        if not customer or not customer.email:
            return ToolResult(status="FAILED", error="Invoice customer has no email address")
        recipient = customer.email
        draft_rows = context.db.query(ToolExecution).filter_by(
            workflow_id=context.workflow_id,
            tool_name="draftInvoiceEmail",
            status="SUCCESS",
        ).order_by(ToolExecution.started_at.desc()).all()
        draft = next((row.output for row in draft_rows if row.output and row.output.get("invoice_id") == invoice_id), None)
        if not draft:
            return ToolResult(status="FAILED", error="No AI-generated email draft found for this invoice")
        subject = draft.get("subject")
        body = draft.get("body")
    
    if not recipient:
        return ToolResult(status="FAILED", error="Missing recipient for email sending")
        
    mode = get_email_mode()
    
    if mode == "sandbox":
        # Check for simulated failures (for generic failure recovery)
        if "invalid" in recipient:
            return ToolResult(status="FAILED", error="Invalid email address (SIMULATED)", verificationMode="SIMULATED")
            
        return ToolResult(
            status="SUCCESS",
            data={"message_id": f"sim-{context.action_id}"},
            verificationMode="SIMULATED"
        )

    if mode != "live":
        return ToolResult(status="FAILED", error="EMAIL_MODE must be either 'sandbox' or 'live'")
    if not subject or not body:
        return ToolResult(status="FAILED", error="Email subject and body are required")

    try:
        response = _send_via_gmail_api(recipient, subject, body)
        message_id = response.get("id")
        invoice = context.db.query(Invoice).filter(Invoice.id == invoice_id).first() if invoice_id else None
        context.db.add(Communication(
            id=str(uuid.uuid4()),
            customer_id=input_data.get("customer_id") or (invoice.customer_id if invoice else None),
            invoice_id=invoice_id,
            channel="EMAIL",
            recipient=recipient,
            subject=subject,
            message=body,
            status="SENT",
        ))
        context.db.commit()
        return ToolResult(
            status="SUCCESS",
            data={"message_id": message_id, "recipient": recipient},
            verificationMode="GMAIL_API_ACCEPTED",
        )
    except FileNotFoundError:
        return ToolResult(status="FAILED", error="Gmail not authorized yet — visit /auth/google/login")
    except Exception as exc:
        context.db.rollback()
        return ToolResult(status="FAILED", error=f"Gmail API send failed: {exc}")

def verify_delivery_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    message_id = input_data.get("message_id")
    mode = get_email_mode()
    
    if mode == "sandbox":
        return ToolResult(
            status="SUCCESS", 
            data={"delivered": True, "opened": False},
            verificationMode="SIMULATED"
        )
    
    return ToolResult(status="FAILED", error="Real verification not implemented")
