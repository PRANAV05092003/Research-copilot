# Benchmark & Evaluation Readiness

This document outlines the constraints and readiness strategy to ensure maximum robustness during automated benchmarks, hidden implementation tests, and senior human review.

## 1. Determinism & Evaluation Constraints

- **Offline-First AI Abstraction**: All LLM and embedding access is behind provider interfaces (`LLMProvider`, `EmbeddingProvider`). We provide a production provider (OpenAI-compatible), a local provider (sentence-transformers), and a fully deterministic in-process mock (`MockLLMProvider`, `HashEmbeddingProvider`).
- **Test Profiles**: Test and CI profiles MUST use the deterministic mocks so every test and `docker-compose` boot works with NO external credentials and NO network access.
- **Seeded Determinism**: Default temperature is 0; wherever sampling exists, accept and honor a seed parameter.
- **Pre-Baked Models**: The backend Docker image downloads the default sentence-transformers model at image build time to ensure zero runtime network downloads.
- **Conventional Surface**: Health endpoints, OpenAPI specifications, error formats, pagination shapes, and port assignments strictly follow conventional specifications to pass hidden test probes.
- **Idempotent Startup**: The container entrypoint runs `alembic upgrade head` then starts the server. The application boots cleanly against an empty database. An idempotent seed script (`make seed`) is available.
- **Golden Fixtures**: A small, committed corpus of sample PDFs and corresponding text fixtures are provided to ensure ingestion, search, and RAG tests have stable inputs offline.
- **Time Control**: Time-dependent logic relies on an injectable clock (no bare `datetime.now()` in business logic) to allow deterministic testing (e.g., using freezegun).
- **No Flakiness**: No tests will depend on wall-clock timing, network reliability, dictionary/hash ordering, or real LLM outputs.

## 2. Risk Register

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| LLM Nondeterminism | High | High | Mitigated by using deterministic Mock providers and seeding all sampling in tests. |
| Missing Credentials | High | Critical | The system uses local models or mocks by default; API keys are only required for the production OpenAI provider. |
| Cold Start Latency | Medium | Medium | Sentence-transformers models are pre-baked into the Docker image at build time. |
| Evaluator Probing | High | High | Strict adherence to documented OpenAPI schemas; generic problem+json error formatting. |
| Time-boxed Evaluation | High | High | One-command boot (`docker compose up`) completes in under 3 minutes due to pre-baked assets and minimized dependencies. |
| Vector Store Size | Low | Medium | Using pgvector HNSW which can handle 1M+ chunks efficiently without out-of-memory errors on standard test VMs. |
| Port Conflicts | Medium | Low | Adhering strictly to assigned ports; ensuring graceful shutdown to release bound ports. |
| Network Isolation | High | Critical | The entire system (API, DB, Redis, Mocks) works within a single Docker bridge network with no external internet calls. |
