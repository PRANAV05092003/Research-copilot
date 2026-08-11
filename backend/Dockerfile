FROM python:3.11-slim as base
# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

FROM base as builder
# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .

# Install dependencies into a separate path /install
# Build wheels, but for PyTorch we want CPU-only
RUN pip install --no-cache-dir --upgrade pip setuptools build && \
    pip wheel --no-deps --wheel-dir /usr/src/app/wheels . && \
    pip install --no-cache-dir --prefix=/install . --extra-index-url https://download.pytorch.org/whl/cpu

FROM base as runtime
WORKDIR /app

# Copy production installed dependencies from builder
COPY --from=builder /install /usr/local

COPY . .

# Download sentence-transformers model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Ensure non-root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
