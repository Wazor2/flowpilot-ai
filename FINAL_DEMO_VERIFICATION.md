# FINAL_DEMO_VERIFICATION

## Current status

FlowPilot AI now has two explicit frontend paths:

- **Demo Mode** (`/workflows/demo-123`): deterministic, local, scripted presentation flow retained for offline demos.
- **Live Workflow Mode** (`/workflows/{workflow-id}`): connected to the FastAPI backend and PostgreSQL-authoritative workflow state.

The live path is created from the New Workflow form with `POST /api/workflows`, then polls workflow state, audit events, and approvals from the backend.

## Live frontend/backend integration

The active live UI uses:

- `POST /api/workflows` to create a workflow from a natural-language objective.
- `GET /api/workflows/{id}` to show status, current step, and current plan.
- `GET /api/workflows/{id}/events` to render the persisted audit trail.
- `GET /api/workflows/{id}/approvals` to load approval requests.
- `POST /api/workflows/{id}/approve` and `/reject` for human decisions.
- CORS configuration through `FRONTEND_ORIGINS`.

Sensitive steps create persisted `Approval` rows and pause the LangGraph executor before tool execution. The live control center refreshes automatically until the workflow reaches a terminal state.

## Backend and AI behavior

- Gemini is the primary structured-output provider.
- OpenAI/OpenRouter fallback is used for rate limits, timeouts, connection failures, and provider unavailability.
- Invalid structured output is retried before falling through.
- Plans are validated with Pydantic and restricted to registered tools.
- Every provider attempt, tool execution, approval, failure, and workflow event is persisted to PostgreSQL-backed tables.
- `MAX_REPLANS` and `MAX_EXECUTION_ATTEMPTS_PER_ACTION` pause workflows at their configured limits.
- `EMAIL_MODE=sandbox` remains the safe default.

Live provider execution requires configured provider keys and a reachable PostgreSQL database. The official tests do not require live AI credentials.

## Verification results

From the repository root:

```bash
PYTHONPATH=. pytest -q tests
npx tsc --noEmit
```

Latest verification:

- **16 Python tests passed**.
- **TypeScript type checking passed**.
- `tests/test_live_api.py` verifies live customer, invoice, and workflow API resources.
- `tests/test_graph_recovery.py` verifies real planner → executor → replan recovery and pause-at-limit behavior.
- Provider tests verify quota fallback and same-provider invalid-output retry.
- Integration tests verify the registered tools and sandboxed email path.

The ESLint command still reports legacy repository-wide lint debt, primarily existing `no-explicit-any` violations and unused variables in older TypeScript modules; this does not block type checking or the Python/API test suite.
