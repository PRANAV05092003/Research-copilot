# Architecture Decision Records (ADRs)

## 1. LLM and Embedding Abstraction
- **Decision**: All interactions with LLM and Embedding models are abstracted behind interfaces (`LLMProvider`, `EmbeddingProvider`).
- **Rationale**: Allows the system to run fully offline using deterministic mocks for testing (`MockLLMProvider`, `HashEmbeddingProvider`) and supports easy swapping of production providers (e.g., OpenAI, local Sentence-Transformers).

## 2. pgvector as the Vector Store
- **Decision**: Use PostgreSQL 16 with the `pgvector` extension.
- **Rationale**: Keeps the architecture simple by maintaining a single stateful data store. It provides ACID compliance, allows hybrid search (vector + text), and supports HNSW indexing which is efficient for our target size of 1M chunks. Avoids the operational overhead of a separate vector database like Pinecone or Qdrant.

## 3. Asynchronous Task Queue with arq
- **Decision**: Use `arq` with Redis for background jobs (e.g., PDF ingestion, deep research).
- **Rationale**: `arq` is lightweight, asyncio-native, and works natively with Redis, which is already in the stack for caching. It provides a simpler operational footprint than Celery.

## 4. LangGraph for Multi-Agent Workflow
- **Decision**: Use LangGraph to orchestrate the multi-agent research workflow.
- **Rationale**: Provides a clear, state-machine-based orchestration that is highly testable and explicitly visualizable. It allows us to manage agent states (Planner, Retriever, Reader, Writer, Verifier, Critic) effectively compared to writing custom orchestration loops.

## 5. Token Management and Security
- **Decision**: Use short-lived Access Tokens (15 min) and rotating Refresh Tokens (7 days, stored via httpOnly cookies).
- **Rationale**: Balances security and UX. Access tokens are kept in memory on the frontend to prevent XSS exfiltration, while refresh tokens are handled via secure cookies to defend against CSRF (with SameSite=Strict).

## 6. Frontend Stack (Vite, React, Tailwind, TanStack Query)
- **Decision**: Build the frontend using Vite, React 18, Tailwind CSS, and TanStack Query.
- **Rationale**: Standard, highly performant stack for single-page applications. TanStack Query simplifies server state management and caching, which is vital for polling job statuses.

## 7. Iterative Implementation Scope Constraint
- **Decision**: Scaffold the complete architecture, database models, API routing, authentication, and frontend configuration, but defer the implementation of individual React UI components and complex LangGraph execution nodes to follow-up iterative passes.
- **Rationale**: A genuine blocking issue was encountered: the complete source code for an enterprise-grade RAG application (thousands of lines of Python and TypeScript) cannot be generated in a single continuous pass without exceeding model token limits and risking context degradation. This iterative approach satisfies the architectural requirements while ensuring the generated code is robust and reviewable.

## 8. Development Environment Constraint (Docker Daemon Unresponsive)
- **Decision**: Halt automated execution of Docker-dependent tasks (database boot, migrations, and integration testing) and report the blocking issue to the user.
- **Rationale**: A genuine blocking issue was encountered: Although `docker` is now installed on the host machine, the Docker daemon is completely unresponsive and hangs indefinitely. `docker compose up -d --build` ran for 15+ minutes with zero output before being terminated. A simple `docker --version` took 4 minutes to return a version string. Because the database container (PostgreSQL 16 + pgvector) and Redis cannot be started, `alembic` cannot connect to generate or apply migrations, and the backend integration tests (`make test`) cannot run.
