# Product Requirements Document

## 1. Functional Requirements (FR)

- **FR-1**: User registration, login, logout, and token refresh.
- **FR-2**: Workspace creation and strictly isolated multi-tenant workspaces.
- **FR-3**: PDF upload (multipart, validation, async ingestion job with status polling).
- **FR-4**: Automatic metadata extraction (title, authors, year, abstract, DOI, venue).
- **FR-5**: Chunking of uploaded documents.
- **FR-6**: Embedding generation and indexing.
- **FR-7**: Natural-language semantic/vector search with top-k and filters across a user's papers.
- **FR-8**: Hybrid (keyword + vector) search capabilities.
- **FR-9**: Conversational RAG chat with conversation history.
- **FR-10**: Per-answer structured citations (claim → paper → chunk → page).
- **FR-11**: Citation verification with machine-readable verdicts.
- **FR-12**: Multi-agent deep-research workflow (plan → retrieve → read → synthesize → verify → critique).
- **FR-13**: Literature review generation across selected papers or a topic.
- **FR-14**: Side-by-side paper comparison (methodology, datasets, metrics, limitations, contributions).
- **FR-15**: Research gap detection from the corpus.
- **FR-16**: Job status tracking for long-running workflows.
- **FR-17**: Health and metrics endpoints for operational observability.

## 2. Non-Functional Requirements (NFR)

### Performance Budgets
- p95 latency < 300 ms for CRUD endpoints.
- p95 latency < 800 ms for search (cached corpus).
- Ingestion of a 20-page PDF < 60 s including embeddings (using deterministic embedder).
- LLM-bound endpoints must stream or return job handles; HTTP never blocks > 30 s.
- Support 100 concurrent users on a single `docker-compose` deployment.
- Initial frontend bundle < 500 KB gzipped.
- Lighthouse performance and accessibility scores >= 90.

### Reliability
- Graceful degradation if Redis or the LLM provider is unavailable:
  - Queue disabled → synchronous fallback still functional.
  - LLM down → 503 with problem+json, CRUD/search unaffected.

## 3. Security Goals
- Adherence to OWASP ASVS L2 and OWASP LLM Top 10.
- Strong password hashing via Argon2id.
- Short-lived access tokens + rotating refresh tokens with reuse detection.
- Strict per-user data isolation (every query scoped by tenant: workspace/user).
- Upload hardening (mime type, size limits, file structure).
- Prompt-injection defenses.
- Secrets managed exclusively via environment variables.
- Full audit trail of auth events.

## 4. Scalability Goals
- Stateless API replicas horizontally scalable.
- CPU-heavy ingestion offloaded to workers via queue.
- Vector index (pgvector HNSW) sized for 1M chunks.
- Caching layers for embeddings and search (Redis).

## 5. Maintainability Goals
- Layers with one-way dependencies (api → services → repositories → db; ai/* behind ports).
- >= 85% test coverage.
- Zero lint errors.
- Full typing (mypy strict-ish: `disallow_untyped_defs`).
- Architecture Decision Records (ADRs) for every significant choice.
- Documentation as deliverable (onboarding friendly).

## 6. Edge Cases
- Empty, corrupt, encrypted, or image-only PDF documents.
- PDFs with > 500 pages or > 25 MB (reject with clear error).
- Duplicate uploads (dedupe by content hash).
- Unicode/CJK text processing.
- Search queries yielding no results or queries on an empty corpus.
- Token overflow of context window (triggering compression path).
- Concurrent uploads of the same file.
- Refresh token theft/replay attempts.
- Citation referencing a chunk not in the evidence set.
- User deletes a paper referenced by an existing conversation (cascade semantics).
- Very long chat history (triggering summarization).
- Query consisting only of stop words (fallback to keyword search).

## 7. Failure Cases
- DB down (readiness endpoint fails, 503 with retry-after).
- Redis down (fallback mode enabled).
- LLM timeout or 5xx (retry with exponential backoff + circuit breaker → structured 503).
- Worker crash mid-ingestion (job marked failed, paper status=failed, user-visible reason).
