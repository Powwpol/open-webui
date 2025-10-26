# Pulsai Backend - Production Dockerfile
# Multi-stage build for optimized image size
# Build from LOCAL files

ARG PYTHON_VERSION=3.11
ARG USE_SLIM=false
ARG BASE_PYTHON=mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}-bookworm

# ============================================
# Stage 1: Builder
# ============================================
FROM ${BASE_PYTHON} AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download embedding models if not SLIM
RUN if [ "$USE_SLIM" != "true" ]; then \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')"; \
    fi

# ============================================
# Stage 2: Runtime
# ============================================
FROM ${BASE_PYTHON}

LABEL maintainer="Pulsai Team"
LABEL description="Pulsai Backend API"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy site-packages from builder to runtime
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code from LOCAL
COPY backend/open_webui /app/backend/open_webui
COPY backend/migrations /app/backend/migrations
COPY backend/alembic.ini /app/backend/alembic.ini
COPY backend/start.sh /app/backend/start.sh

# Copy configuration
COPY config /app/config

# Create data directory
RUN mkdir -p /app/backend/data && \
    chmod 755 /app/backend/data && \
    chmod +x /app/backend/start.sh

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run as non-root user (security)
# Use UID 1001 to avoid conflict with existing user in base image
RUN useradd -m -u 1001 pulsai && \
    chown -R pulsai:pulsai /app
USER pulsai

# Set working directory for app
WORKDIR /app/backend

# Start application
CMD ["bash", "start.sh"]

