import datetime
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["EMAIL_MODE"] = "sandbox"

from backend.database import Base, get_db
from backend.main import app
from backend.models import Customer, Invoice, Workflow
from backend.tool_registry import ToolContext
from backend.tools import registry

engine = create_engine(
    os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Seed data
    c = Customer(id="cust-1", name="Acme Corp", email="contact@acme.com")
    i = Invoice(id="inv-1", invoice_number="INV-1004", customer_id="cust-1", amount=100.0, due_date=datetime.datetime(2023, 1, 1))
    session.add(c)
    session.add(i)
    session.commit()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_integration_flow(db_session):
    # Create Workflow
    wf = Workflow(id="wf-test-1", objective="Test")
    db_session.add(wf)
    db_session.commit()
    
    context = ToolContext(workflow_id="wf-test-1", step_id="step-1", action_id="act-1", db=db_session)
    
    # Query InvoiceTool
    res = registry.execute_tool("getInvoice", {"invoice_id": "inv-1"}, context)
    assert res.status == "SUCCESS"
    assert res.data["invoice_number"] == "INV-1004"
    
    # Query CustomerTool
    res = registry.execute_tool("getCustomer", {"customer_id": "cust-1"}, context)
    assert res.status == "SUCCESS"
    
    # Execute EmailTool (Sandbox)
    context.action_id = "act-email-1"
    res = registry.execute_tool("sendEmail", {"recipient": "contact@acme.com", "subject": "Test", "body": "Body"}, context)
    assert res.status == "SUCCESS"
    assert res.verificationMode == "SIMULATED"
    
    # Verify action
    context.action_id = "act-verify-1"
    res = registry.execute_tool("verifyAction", {"action": "email_sent"}, context)
    assert res.status == "SUCCESS"

def test_failure_recovery_flow(db_session):
    wf = Workflow(id="wf-test-2", objective="Test Recovery")
    db_session.add(wf)
    db_session.commit()
    
    context = ToolContext(workflow_id="wf-test-2", step_id="step-1", action_id="act-fail-1", db=db_session)
    
    # Email failure
    res = registry.execute_tool("sendEmail", {"recipient": "invalid@acme.com", "subject": "Test", "body": "Body"}, context)
    assert res.status == "FAILED"
    
    # Retrieve alternate contacts
    context.action_id = "act-alt-contact"
    res = registry.execute_tool("getCustomerContacts", {"customer_id": "cust-1"}, context)
    assert res.status == "SUCCESS"
    
    # Assuming the recovery logic selects another contact, we execute recovery action
    context.action_id = "act-email-2"
    res = registry.execute_tool("sendEmail", {"recipient": "billing@acme.com", "subject": "Test", "body": "Body"}, context)
    assert res.status == "SUCCESS"
