# FlowPilot AI provider setup

The Python agent layer now routes all structured planning calls through `AIProviderManager`. Gemini is attempted first; OpenAI is tried automatically after Gemini quota/429, timeout, connection, or service-unavailable failures. Malformed structured output is retried once on the same provider before the manager proceeds to the next provider. If every configured provider fails, the LangGraph state becomes `PAUSED` with a manual-intervention reason; no unvalidated plan is executed.

Set `DATABASE_URL` to the authoritative PostgreSQL database and configure at least `GEMINI_API_KEY`. Configure `OPENAI_API_KEY` to enable automatic fallback. `EMAIL_MODE=sandbox` remains the safe default. File-backed SQLite and the legacy JSON audit log are not valid production storage; only `sqlite:///:memory:` is accepted by the test suite.

The runtime records each provider attempt in `ai_runs` and `audit_events`, and records tool, approval, failure, and workflow events in `audit_events`. Apply the Alembic migration before using an existing PostgreSQL database:

```bash
cd backend
alembic upgrade head
```

The runtime guards are configurable through `MAX_REPLANS` (default `3`) and `MAX_EXECUTION_ATTEMPTS_PER_ACTION` (default `2`). Reaching either limit pauses the workflow and records the reason.

Focused verification from the repository root:

```bash
PYTHONPATH=. pytest -q tests/test_ai_provider_resilience.py tests/test_graph_recovery.py tests/integration_test.py
```

`tests/test_graph_recovery.py` uses fake structured-output providers and test-only registered tools to exercise the real planner → executor → replan graph. It verifies both injected-failure recovery and the transition to `PAUSED` when the replan limit is exceeded, without requiring live LLM keys.

The deterministic Demo Mode/frontend path is unchanged; only AI Mode uses the provider manager.
