from __future__ import annotations

import datetime
import json
import os
import uuid
from unittest.mock import MagicMock

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from agents.nodes import executor, planner
from agents.state import PlanStep, State, ToolExecutionResult
from backend.database import Base
from backend.models import AuditEvent, Customer, Invoice, ToolExecution, Workflow
from backend.tool_registry import ToolContext
from backend.tools import registry
from backend.tools import email_tool
import utils.audit_logger as audit_logger_module


def _database(monkeypatch):
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    monkeypatch.setattr(executor, "SessionLocal", factory)
    monkeypatch.setattr(planner, "SessionLocal", factory)
    monkeypatch.setattr(audit_logger_module, "SessionLocal", factory)
    return factory, test_engine


def test_pre_execution_recheck_cancels_paid_invoice_send(monkeypatch):
    factory, test_engine = _database(monkeypatch)
    workflow_id = f"wf-stale-{uuid.uuid4()}"
    with factory() as db:
        db.add(Workflow(id=workflow_id, objective="Remind on overdue invoice"))
        db.add(Customer(id="cust-stale", name="Jane Doe", email="jane@example.test"))
        db.add(Invoice(
            id="inv-stale", invoice_number="INV-9", customer_id="cust-stale",
            amount=90, due_date=datetime.datetime(2025, 1, 1), status="PAID",
        ))
        db.commit()

    execute = MagicMock(side_effect=AssertionError("sendEmail must not execute for a paid invoice"))
    monkeypatch.setattr(registry, "execute_tool", execute)
    state = State(
        workflow_id=workflow_id,
        objective="Send reminder",
        status="APPROVED",
        plan=[PlanStep(
            tool="sendEmail",
            arguments={"invoice_id": "inv-stale"},
            reason="Send invoice reminder",
            requires_approval=True,
        )],
    )

    result = executor.executor_node(state)
    assert result.status == "COMPLETED"
    assert result.completed_actions[-1].status == "CANCELLED"
    assert execute.call_count == 0
    with factory() as db:
        assert db.query(Workflow).filter_by(id=workflow_id).one().status == "RESOLVED"
        event = db.query(AuditEvent).filter_by(
            workflow_id=workflow_id,
            event_type="PRE_EXECUTION_SEND_CANCELLED",
        ).one()
        assert event.reason and "PAID" in event.reason
    test_engine.dispose()


def test_planner_redacts_customer_pii_from_provider_payload(monkeypatch):
    factory, test_engine = _database(monkeypatch)
    with factory() as db:
        db.add(Customer(
            id="cust-private", name="Jane Doe", email="jane.doe@example.test", phone="+1 555 222 1234"
        ))
        db.commit()

    captured = {}

    def inspect_prompt(*args, **kwargs):
        captured["prompt"] = kwargs["user_prompt"]
        raise RuntimeError("stop after prompt capture")

    monkeypatch.setattr(planner, "generate_structured", inspect_prompt)
    state = State(
        workflow_id=f"wf-privacy-{uuid.uuid4()}",
        objective="Review Jane Doe at jane.doe@example.test, phone +1 555 222 1234",
        completed_actions=[ToolExecutionResult(
            tool_name="getCustomer",
            arguments={"customer_id": "cust-private"},
            result={
                "customer_id": "cust-private", "name": "Jane Doe", "email": "jane.doe@example.test",
                "phone": "+1 555 222 1234", "risk_level": "HIGH", "days_overdue": 30, "amount": 80,
                "subject": "Reminder to Jane Doe", "body": "Hello Jane Doe",
            },
            status="SUCCESS",
        )],
    )
    planner.planner_node(state)
    prompt = captured["prompt"]
    assert "Jane Doe" not in prompt
    assert "jane.doe@example.test" not in prompt
    assert "555 222 1234" not in prompt
    assert "HIGH" in prompt and "days_overdue" in prompt and "amount" in prompt
    test_engine.dispose()


def test_duplicate_action_id_cannot_send_email_twice(monkeypatch, tmp_path):
    factory, test_engine = _database(monkeypatch)
    workflow_id = f"wf-idempotent-{uuid.uuid4()}"
    with factory() as db:
        db.add(Workflow(id=workflow_id, objective="Email test"))
        db.commit()
        context = ToolContext(
            workflow_id=workflow_id,
            step_id="send-1",
            action_id=str(uuid.uuid4()),
            db=db,
        )
        token_file = tmp_path / ".gmail_token.json"
        token_file.write_text('{"refresh_token":"test-refresh-token"}', encoding="utf-8")
        monkeypatch.setattr(email_tool, "GMAIL_TOKEN_PATH", token_file)
        credentials = MagicMock()
        monkeypatch.setattr(email_tool, "Credentials", MagicMock(return_value=credentials))
        gmail_service = MagicMock()
        gmail_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "id": "gmail-message-id"
        }
        build_service = MagicMock(return_value=gmail_service)
        monkeypatch.setattr(email_tool, "build", build_service)
        monkeypatch.setenv("EMAIL_MODE", "live")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
        args = {"recipient": "billing@example.test", "subject": "Invoice", "body": "Reminder"}

        first = registry.execute_tool("sendEmail", args, context)
        replay = registry.execute_tool("sendEmail", args, context)
        assert first.status == "SUCCESS"
        assert replay.status == "SUCCESS"
        assert replay.verificationMode == "IDEMPOTENT_REPLAY"
        assert replay.data["idempotent_replay"] is True
        gmail_service.users.return_value.messages.return_value.send.assert_called_once()
        assert db.query(ToolExecution).filter_by(action_id=context.action_id, tool_name="sendEmail").count() == 1
    test_engine.dispose()
