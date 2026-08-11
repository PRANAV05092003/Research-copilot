# Definition of Done

This document provides the Definition of Done (DoD) for the Research Copilot implementation. A phase is considered complete only when its verification commands pass.

## 1. Automated Verification Checks

The following commands MUST pass successfully:
- [ ] `make test`: Runs unit, API, and integration tests.
- [ ] `make lint`: Validates code style and quality (e.g., ruff, eslint).
- [ ] `make typecheck`: Validates strict typing (e.g., mypy, tsc).
- [ ] `make frontend-checks`: Runs frontend tests and bundle size verifications.
- [ ] `make build`: Successfully builds all Docker images.
- [ ] `docker compose up`: The system boots successfully from a clean state.

## 2. System Functionality (Smoke Tests)

- [ ] A `scripts/smoke_test.py` script successfully hits health endpoints, registers a user, logs in, uploads a fixture PDF, and executes a search query.
- [ ] The system operates entirely offline using deterministic mocks (No network access required).

## 3. Code Quality & Security

- [ ] Test coverage is >= 85%.
- [ ] There are zero hardcoded secrets or passwords in the codebase.
- [ ] All architectural decisions and deviations from the spec are documented in `docs/DECISIONS.md`.
- [ ] Documentation is complete, including `README.md`, `ARCHITECTURE.md`, `API.md`, and this `DEFINITION_OF_DONE.md`.

## 4. Feature Completeness

- [ ] All functional requirements (FR-1 through FR-17) are implemented and functional.
- [ ] Edge cases and failure cases are explicitly handled and tested.
- [ ] Error messages conform to the RFC 7807 `application/problem+json` standard.
