from __future__ import annotations

import datetime
import os
import uuid
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


def test_live_email_sends_with_gmail_smtp_and_records_communication(monkeypatch):
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
        smtp_instance = MagicMock()
        smtp_instance.send_message.return_value = {}
        smtp_factory = MagicMock()
        smtp_factory.return_value.__enter__.return_value = smtp_instance
        monkeypatch.setattr(email_tool.smtplib, "SMTP", smtp_factory)
        monkeypatch.setenv("EMAIL_MODE", "live")
        monkeypatch.setenv("EMAIL_SMTP_USER", "ommanjules@gmail.com")
        monkeypatch.setenv("EMAIL_APP_PASSWORD", "abcd efgh ijkl mnop")

        result = email_tool.send_email_execute({
            "recipient": "billing@acme.test",
            "subject": "Invoice INV-43 reminder",
            "body": "Please review your invoice.",
            "invoice_id": "inv-send",
        }, context)

        assert result.status == "SUCCESS"
        assert result.verificationMode == "SMTP_ACCEPTED"
        smtp_factory.assert_called_once_with("smtp.gmail.com", 587, timeout=30.0)
        smtp_instance.starttls.assert_called_once_with()
        smtp_instance.login.assert_called_once_with("ommanjules@gmail.com", "abcdefghijklmnop")
        smtp_instance.send_message.assert_called_once()
        sent = smtp_instance.send_message.call_args.args[0]
        assert sent["To"] == "billing@acme.test"
        assert sent["Subject"] == "Invoice INV-43 reminder"
        communication = db.query(Communication).filter_by(invoice_id="inv-send").one()
        assert communication.status == "SENT"
    finally:
        db.close()


def test_live_email_requires_app_password(monkeypatch):
    monkeypatch.setenv("EMAIL_MODE", "live")
    monkeypatch.setenv("EMAIL_SMTP_USER", "ommanjules@gmail.com")
    monkeypatch.delenv("EMAIL_APP_PASSWORD", raising=False)
    result = email_tool.send_email_execute({
        "recipient": "billing@acme.test", "subject": "Invoice", "body": "Reminder"
    }, MagicMock())
    assert result.status == "FAILED"
    assert "EMAIL_APP_PASSWORD" in result.error
