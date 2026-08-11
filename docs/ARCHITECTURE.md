# Architecture Design

## System Context Diagram
```mermaid
graph TD
    User([User]) -->|HTTPS| WebServer[Nginx Web Server]
    WebServer -->|Static Files| Frontend[React SPA]
    WebServer -->|/api/v1| API[FastAPI Backend]
    API -->|Read/Write| DB[(PostgreSQL + pgvector)]
    API -->|Cache / Queue| Cache[(Redis)]
    API -->|LLM Requests| LLM[LLM Provider]
    Worker[Arq Worker] -->|Listen| Cache
    Worker -->|Read/Write| DB
    Worker -->|Embeddings| Embedding[Embedding Provider]
    Worker -->|LLM Requests| LLM
```

## Container Diagram
```mermaid
graph TD
    subgraph "Docker Compose"
        Nginx[Nginx]
        Backend[FastAPI App]
        Worker[Arq Worker]
        DB[(PostgreSQL 16)]
        Redis[(Redis)]
    end
    Nginx -->|Reverse Proxy| Backend
    Backend --> DB
    Backend --> Redis
    Worker --> DB
    Worker --> Redis
```

## Request Flow (PDF Ingestion)
```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant D as DB
    participant R as Redis (Queue)
    participant W as Worker
    
    U->>A: POST /papers/upload (PDF)
    A->>D: Create Paper (Status: Pending)
    A->>R: Enqueue `ingest_paper` job
    A-->>U: 202 Accepted (Job ID)
    
    W->>R: Dequeue `ingest_paper`
    W->>D: Update Status (Processing)
    W->>W: Parse PDF & Extract Metadata
    W->>W: Chunk Text
    W->>W: Generate Embeddings
    W->>D: Save Chunks & Embeddings
    W->>D: Update Status (Ready)
```

## Agent Graph Workflow
```mermaid
graph TD
    Start[User Query] --> Planner[Planner Agent]
    Planner -->|Generate Sub-queries| Retriever[Retriever Agent]
    Retriever -->|Search pgvector| Reader[Reader Agent]
    Reader -->|Extract Evidence| Writer[Writer Agent]
    Writer -->|Draft with Citations| Verifier[Verifier Agent]
    Verifier -->|Check Entailment| Critic[Critic Agent]
    Critic -->|Pass| End[Final Response]
    Critic -->|Needs Revision| Retriever
```

## Deployment Architecture
- **Single-Host Docker Compose**: Runs Nginx, API, Worker, PostgreSQL, and Redis.
- **Scale-Out Path**: The API and Worker are stateless. Nginx acts as a load balancer for multiple API replicas. PostgreSQL and Redis can be moved to managed services (e.g., RDS, ElastiCache) for production scale.
