from __future__ import annotations

import datetime
import base64
import os
import uuid
from email import policy
from email.parser import BytesParser
from pathlib import Path
from unittest.mock import MagicMock

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from agents.state import State
from backend.database import Base, SessionLocal, engine
from backend.models import Communication, Customer, Invoice, ToolExecution, Workflow
from backend.tool_registry import ToolContext
from backend.tools import email_tool


def _context(db):
    workflow_id = str(uuid.uuid4())
    db.add(Workflow(id=workflow_id, objective="Send invoice reminder"))
    db.commit()
    return ToolContext(
        workflow_id=workflow_id,
        step_id="email-step",
        action_id=str(uuid.uuid4()),
        db=db,
    )


def test_draft_invoice_email_uses_structured_ai_output(monkeypatch):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add(Customer(id="cust-draft", name="Acme", email="billing@acme.test"))
        db.add(Invoice(
            id="inv-draft",
            invoice_number="INV-42",
            customer_id="cust-draft",
            amount=125.50,
            due_date=datetime.datetime(2025, 1, 1),
            status="OVERDUE",
            days_overdue=14,
        ))
        db.commit()
        context = _context(db)
        generated = {}

        def fake_generate(workflow_id, **kwargs):
            generated.update(kwargs)
            return email_tool.InvoiceEmailDraft(
                subject="A note about invoice INV-42",
                body="Hello Acme, could you please review invoice INV-42?",
            )

        monkeypatch.setattr(email_tool, "generate_structured", fake_generate)
        result = email_tool.draft_invoice_email_execute({"invoice_id": "inv-draft"}, context)
        assert result.status == "SUCCESS"
        assert result.data["recipient"] == "billing@acme.test"
        assert result.data["subject"] == "A note about invoice INV-42"
        assert "INV-42" in generated["user_prompt"]
        assert generated["response_schema"] is email_tool.InvoiceEmailDraft
    finally:
        db.close()


def test_live_email_sends_through_gmail_api_and_records_communication(monkeypatch, tmp_path):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add(Customer(id="cust-send", name="Acme", email="billing@acme.test"))
        db.add(Invoice(
            id="inv-send",
            invoice_number="INV-43",
            customer_id="cust-send",
            amount=75,
            due_date=datetime.datetime(2025, 1, 1),
        ))
        db.commit()
        context = _context(db)
        db.add(ToolExecution(
            id=str(uuid.uuid4()),
            workflow_id=context.workflow_id,
            tool_name="draftInvoiceEmail",
            input={"invoice_id": "inv-send"},
            output={
                "invoice_id": "inv-send",
                "subject": "Invoice INV-43 reminder",
                "body": "Please review your invoice.",
            },
            status="SUCCESS",
        ))
        db.commit()
        token_file = tmp_path / ".gmail_token.json"
        token_file.write_text('{"refresh_token":"test-refresh-token"}', encoding="utf-8")
        monkeypatch.setattr(email_tool, "GMAIL_TOKEN_PATH", token_file)
        credentials = MagicMock()
        monkeypatch.setattr(email_tool, "Credentials", MagicMock(return_value=credentials))
        build_service = MagicMock()
        gmail_service = build_service.return_value
        gmail_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "id": "gmail-message-id"
        }
        monkeypatch.setattr(email_tool, "build", build_service)
        monkeypatch.setenv("EMAIL_MODE", "live")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")

        result = email_tool.send_email_execute({
            "recipient": "billing@acme.test",
            "subject": "Invoice INV-43 reminder",
            "body": "Please review your invoice.",
            "invoice_id": "inv-send",
        }, context)

        assert result.status == "SUCCESS"
        assert result.verificationMode == "GMAIL_API_ACCEPTED"
        assert result.data["message_id"] == "gmail-message-id"
        credentials.refresh.assert_called_once()
        build_service.assert_called_once_with("gmail", "v1", credentials=credentials, cache_discovery=False)
        send_request = gmail_service.users.return_value.messages.return_value.send
        send_request.assert_called_once()
        assert send_request.call_args.kwargs["userId"] == "me"
        raw = send_request.call_args.kwargs["body"]["raw"]
        raw += "=" * (-len(raw) % 4)
        sent = BytesParser(policy=policy.default).parsebytes(base64.urlsafe_b64decode(raw))
        assert sent["To"] == "billing@acme.test"
        assert sent["Subject"] == "Invoice INV-43 reminder"
        assert sent.get_content().strip() == "Please review your invoice."
        communication = db.query(Communication).filter_by(invoice_id="inv-send").one()
        assert communication.status == "SENT"
    finally:
        db.close()


def test_live_email_requires_gmail_authorization(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MODE", "live")
    monkeypatch.setattr(email_tool, "GMAIL_TOKEN_PATH", tmp_path / ".gmail_token.json")
    result = email_tool.send_email_execute({
        "recipient": "billing@acme.test", "subject": "Invoice", "body": "Reminder"
    }, MagicMock())
    assert result.status == "FAILED"
    assert result.error == "Gmail not authorized yet — visit /auth/google/login"
