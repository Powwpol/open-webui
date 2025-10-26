# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base
WORKDIR /app

# Builder stage: install dependencies in a venv
FROM base AS builder

# Copy only requirements.txt first for better cache usage
COPY --link requirements.txt ./

# Create virtual environment and install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install -r requirements.txt

# Copy the rest of the backend code
COPY --link . ./

# Final stage: minimal runtime image
FROM base AS final
WORKDIR /app

# Create non-root user
RUN useradd -m webuiuser
USER webuiuser

# Copy app code and venv from builder
COPY --from=builder /app /app
COPY --from=builder /app/.venv /app/.venv

# Set PATH to use the venv
ENV PATH="/app/.venv/bin:$PATH"

# Expose port (adjust as needed, e.g. 8080 or 8000)
EXPOSE 8080

# Default command (adjust as needed, e.g. start.sh or main.py)
CMD ["/app/start.sh"]

# Notes:
# - .env files, .git, and other secrets/configs should be excluded via .dockerignore
# - If you want to run with gunicorn/uvicorn, adjust CMD accordingly
# - If you need to pass runtime environment variables, do so via docker run -e ...
