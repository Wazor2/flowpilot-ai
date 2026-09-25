from __future__ import annotations

import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["EMAIL_MODE"] = "sandbox"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import Workflow

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_customer_and_invoice_resources_are_live():
    customer_response = client.post("/api/customers", json={
        "name": "API Test Customer",
        "email": f"api-{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+91 90000 00000",
    })
    assert customer_response.status_code == 200
    customer = customer_response.json()

    invoice_response = client.post("/api/invoices", json={
        "customer_id": customer["id"],
        "amount": 125000,
        "due_date": "2026-10-15",
        "status": "OVERDUE",
    })
    assert invoice_response.status_code == 200
    invoice = invoice_response.json()
    assert invoice["customer_id"] == customer["id"]
    assert invoice["amount"] == 125000

    assert any(item["id"] == customer["id"] for item in client.get("/api/customers").json())
    assert any(item["id"] == invoice["id"] for item in client.get("/api/invoices").json())


def test_workflow_list_endpoint_returns_database_records():
    workflow_id = f"wf-api-{uuid.uuid4()}"
    db = TestingSessionLocal()
    try:
        db.add(Workflow(id=workflow_id, objective="API list test", mode="AUTONOMOUS"))
        db.commit()
    finally:
        db.close()

    response = client.get("/api/workflows")
    assert response.status_code == 200
    assert any(item["id"] == workflow_id for item in response.json())
