# research-copilot

Multi-agent AI research copilot with RAG, pgvector hybrid search, LangGraph, and citation verification.

## Project Overview
Research Copilot is an enterprise-grade, multi-tenant web application designed to accelerate scientific and academic research. By fusing semantic vector search with deterministic agentic workflows, the platform enables users to upload thousands of pages of research, query across complex corpuses, and generate highly reliable, deeply verified literature reviews and summaries.

## Key Capabilities
- **Strictly Isolated Multi-Tenancy**: Upload and query papers securely per user, isolated into distinct workspaces.
- **Verifiable Citations**: Chatbot answers are grounded in specific document chunks. A multi-tier entailment check prevents hallucinations by verifying that retrieved sources truly support generated claims.
- **Deep Research Workflow**: Execute a multi-agent orchestration (Planner → Retriever → Reader → Writer → Verifier → Critic) using LangGraph to analyze complex topics and synthesize comprehensive research reports.
- **Hybrid Search Architecture**: Fuses dense vector embeddings (pgvector) and sparse keyword search (tsvector) using Reciprocal Rank Fusion (RRF) for optimal recall.

## Architecture
The application follows a clean, decoupled architecture:
1. **API Gateway & Core Logic**: A high-performance asynchronous REST API.
2. **Vector Engine**: PostgreSQL infused with the `pgvector` extension for storing 384-dimensional dense text embeddings.
3. **Task Queue**: Redis-backed ARQ queues for handling long-running background tasks (PDF chunking, Embedding generation, LangGraph literature reviews).
4. **Client Interface**: A responsive Single Page Application (SPA).

## Technology Stack
- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0, PostgreSQL 16 (`pgvector`), Redis (Arq worker), LangGraph, Pydantic, Alembic.
- **Frontend**: TypeScript, React 18, Vite, Tailwind CSS, TanStack Query.
- **AI & ML**: Sentence-Transformers (`all-MiniLM-L6-v2`), OpenAI API compatibility.

## Core Workflow
1. **Ingestion**: Users upload PDFs which are background-processed into semantically chunked text blocks and embedded into vector space.
2. **Retrieval**: Users converse with the copilot. Queries are embedded and executed against PostgreSQL via Hybrid Search.
3. **Generation**: An LLM agent formulates responses based on retrieved context, injecting inline citations.
4. **Verification**: A strict critic agent verifies every single citation against the origin text before the payload is returned to the user.

## Installation

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.13 (for local backend development)

### Environment Configuration
Copy the example environment template and configure your secrets:
```bash
cp .env.example .env
```
Ensure that `JWT_SECRET_KEY` is replaced with a securely generated 32+ character string in production. By default, `LLM_PROVIDER` is set to `mock` for deterministic local testing. Set it to `openai` and provide an `OPENAI_API_KEY` for live model generation.

## Docker Deployment (Production & Staging)
The absolute easiest way to boot the stack is via Docker.
```bash
# Build images and start detached containers
docker compose up -d --build
```
This automatically boots PostgreSQL, Redis, the API server on `:8000`, the ARQ background worker, and the React frontend on `:5173`. Database migrations are executed via the CI pipeline or manually.

## Local Development
For native local development outside of Docker:
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# Frontend Setup
cd frontend
npm install
npm run dev
```

## Testing
The repository features exhaustive test coverage encompassing E2E integration tests, backend unit tests, and frontend interface tests.

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm run test
```

## CI/CD
A fully integrated GitHub Actions pipeline (`.github/workflows/rc3_validation.yml`) enforces the deployment lifecycle. On every push to `main`, the CI runner executes:
1. Static analysis (`ruff`, `mypy`, `eslint`, `tsc`).
2. Security Vulnerability Scanning (`bandit`, `pip-audit`).
3. Clean container build isolating production dependencies from development tooling.
4. End-to-End (`e2e_validation.py`) integration suite against a live PostgreSQL container checking pgvector assertions and citation graph schemas.

## Security
- **Authentication**: Stateless, secure JWT implementations featuring short-lived access tokens and rotated, HTTP-Only refresh tokens.
- **Dependency Isolation**: Docker multi-stage builds actively drop testing and development utilities (like `pytest` and `mypy`) preventing them from leaking into the runtime container.
- **Strict Validations**: All configurations are protected via Pydantic model validators (e.g. failing runtime if mock configurations are detected in production).
- **Security Check**: `pip-audit` runs independently on both the development requirements and the final compiled production image.

## Project Structure
```text
research-copilot/
├── backend/            # FastAPI python backend
│   ├── app/            # Core application logic
│   ├── alembic/        # Database migrations
│   ├── scripts/        # Utility & validation scripts
│   └── tests/          # Pytest suites
├── frontend/           # React frontend
│   ├── src/            # Components, hooks, and services
│   └── tests/          # Vitest suites
├── infra/              # Infrastructure & cloud configurations
├── docs/               # Architecture documents and ADRs
└── .github/workflows/  # CI/CD orchestration
```

## API Overview
Core domains:
- `/api/v1/auth`: Authentication operations (Register, Login, Refresh, Logout).
- `/api/v1/papers`: File ingestion and status tracking.
- `/api/v1/search`: Hybrid semantic search endpoint.
- `/api/v1/conversations`: Chat sessions and LangGraph RAG executions.
- `/api/v1/research`: Deep multi-agent literature reviews.

## Limitations
- GPU acceleration is disabled in the standard Dockerfile (`torch` installed via the CPU-only index) to optimize image size by ~2GB. If deploying on hardware with NVIDIA drivers, modify the `Dockerfile` to include standard PyTorch binaries.
- Production readiness is gated behind the CI/CD pipeline's E2E success. Do not tag the release without verifying pipeline artifacts.

## License
MIT License.
