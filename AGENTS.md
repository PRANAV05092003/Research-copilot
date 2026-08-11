# Agent Guidelines for Research Copilot

This document outlines how future coding agents should interact with this repository.

1. **Strict Type Checking**: The backend enforces `mypy` with strict checking. All functions must have type hints for arguments and return types.
2. **Testing Constraints**: Every unit test MUST execute fully offline. The default `LLM_PROVIDER` and `EMBEDDING_PROVIDER` must be set to `mock`. Any tests that hit an external provider must be explicitly marked and skipped in CI.
3. **Database Usage**: Do not use `Base.metadata.create_all()` in production code. Use Alembic for all schema migrations.
4. **Agent Workflow**: The multi-agent capabilities are built using LangGraph. Adding a new agent requires modifying the graph definition in `backend/app/ai/agents/graph.py` and creating a new node in the `nodes/` directory.
5. **Linting**: The backend uses `ruff` and the frontend uses `eslint` and `prettier`. Run `make lint` before pushing any code.
