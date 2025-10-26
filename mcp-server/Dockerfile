# Multi-stage Dockerfile for Pulsai MCP Server

FROM python:3.11-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml ./
COPY pulsai_mcp/ ./pulsai_mcp/

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --without dev --no-interaction --no-ansi

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY pulsai_mcp/ ./pulsai_mcp/

# Expose port
EXPOSE 8400

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8400/health').raise_for_status()"

# Run server
CMD ["python", "-m", "pulsai_mcp.server"]

