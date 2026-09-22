# Backend API Contracts

This document outlines the API contracts for the FlowPilot backend, which is built in Python using FastAPI and SQLAlchemy.

## Internal Python Contract (Person 1 - AI Agent)

Person 1 can interact with the backend using the `ToolRegistry` and `ToolContext` available in `backend.tool_registry`.

```python
from backend.tools import registry
from backend.tool_registry import ToolContext

# List all available tools
tools = registry.list_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Execute a tool
context = ToolContext(workflow_id="wf-123", step_id="step-1", action_id="act-1", db=session)
result = registry.execute_tool("getInvoice", {"invoice_id": "INV-1004"}, context)

if result.status == "SUCCESS":
    print(result.data)
else:
    print(result.error)
```

## External REST API Contract (Person 3 - Frontend UI)

The backend exposes REST APIs using FastAPI for the frontend dashboard and management interfaces.

### `POST /api/workflows`
Creates a new workflow.
- **Payload:** `{"objective": "string", "mode": "AUTONOMOUS | HITL"}`
- **Response:** `{"id": "workflow-uuid", "status": "IN_PROGRESS"}`

### `GET /api/workflows/{id}`
Gets the current status of a workflow.

### `GET /api/workflows/{id}/events`
Gets the complete audit log for a specific workflow.

### `POST /api/workflows/{id}/approve`
Approves an action waiting for approval in a workflow.
- **Payload:** `{"approval_id": "uuid", "actor": "user@company.com"}`
- **Response:** `{"status": "APPROVED"}`

### `POST /api/workflows/{id}/reject`
Rejects an action waiting for approval.
- **Payload:** `{"approval_id": "uuid", "actor": "user@company.com"}`
- **Response:** `{"status": "REJECTED"}`

### `POST /api/workflows/{id}/replan`
Logs a replan event when the AI encounters a failure.
- **Payload:** `{"trigger": "string", "failure_context": {}, "new_plan": {}}`

### Resource Endpoints
- `GET /api/invoices` - List all invoices
- `GET /api/customers` - List all customers
