# 🐳 Pulsai Docker Guide

Complete guide to containerize and deploy Pulsai with Docker.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Images](#images)
3. [Build Commands](#build-commands)
4. [Docker Compose](#docker-compose)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/pulsai.git
cd pulsai

# 2. Create config directory
mkdir -p config
cp config/mcp-servers.yaml.example config/mcp-servers.yaml

# 3. Start all services
docker-compose -f docker-compose.pulsai.yaml up -d

# 4. Check logs
docker-compose -f docker-compose.pulsai.yaml logs -f

# 5. Access Pulsai
open http://localhost:8080
```

### Option 2: Build Images First

```bash
# Linux/macOS
./build-pulsai.sh --tag v1.0.0

# Windows
build-pulsai.bat --tag v1.0.0

# Then start with Docker Compose
docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## 📦 Images

### Pulsai Backend (`pulsai/backend`)

**Full-featured FastAPI backend:**
- ✅ All features (RAG, embeddings, chat, functions)
- ✅ Ollama integration
- ✅ vLLM support
- ✅ MCP client hub
- ✅ Recursive chats & auto fine-tuning
- ✅ Quality scoring
- ✅ Webhook events (n8n)

**Base:** `python:3.11-slim-bookworm`  
**Port:** `8080`  
**Size:** ~2.5GB (full), ~1.2GB (slim)

### Pulsai MCP Server (`pulsai/mcp`)

**Custom Model Context Protocol server:**
- ✅ Recursive chat tools
- ✅ Model information tools
- ✅ Context summary tools
- ✅ FastAPI-based

**Base:** `python:3.11-slim-bookworm`  
**Port:** `8001`  
**Size:** ~500MB

---

## 🔨 Build Commands

### Build Scripts

Both Linux/macOS and Windows scripts are provided.

#### Linux/macOS: `build-pulsai.sh`

```bash
# Basic build
./build-pulsai.sh

# Build with GPU support
./build-pulsai.sh --cuda

# Build slim version (no embedding models)
./build-pulsai.sh --slim

# Build with custom tag
./build-pulsai.sh --tag v1.2.3

# Build without cache (clean build)
./build-pulsai.sh --no-cache

# Build and push to registry
./build-pulsai.sh --tag v1.0.0 --push

# Combine options
./build-pulsai.sh --cuda --tag v2.0.0 --push
```

#### Windows: `build-pulsai.bat`

```cmd
REM Basic build
build-pulsai.bat

REM Build with GPU support
build-pulsai.bat --cuda

REM Build with custom tag
build-pulsai.bat --tag v1.2.3

REM Build and push
build-pulsai.bat --tag v1.0.0 --push
```

### Manual Docker Build

#### Backend

```bash
docker build \
  --build-arg USE_CUDA=false \
  --build-arg USE_SLIM=false \
  --build-arg BUILD_HASH=$(git rev-parse --short HEAD) \
  -t pulsai/backend:latest \
  -f Dockerfile \
  .
```

#### MCP Server

```bash
docker build \
  -t pulsai/mcp:latest \
  -f mcp-server/Dockerfile \
  mcp-server/
```

---

## 🎼 Docker Compose

### Services Architecture

```
┌─────────────────────────────────────────────────┐
│                  Pulsai Stack                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐       ┌──────────────┐      │
│  │   Backend    │◄──────┤    Redis     │      │
│  │  (FastAPI)   │       │   (Cache)    │      │
│  └──────┬───────┘       └──────────────┘      │
│         │                                       │
│         │                                       │
│  ┌──────▼───────┐       ┌──────────────┐      │
│  │    Ollama    │       │  MCP Server  │      │
│  │ (Local LLM)  │       │  (Protocol)  │      │
│  └──────────────┘       └──────────────┘      │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Configuration: `docker-compose.pulsai.yaml`

```yaml
services:
  pulsai-backend:  # Main application
  pulsai-redis:    # Cache & sessions
  pulsai-ollama:   # Local LLM inference
  pulsai-mcp:      # Custom MCP server
```

### Basic Commands

```bash
# Start all services
docker-compose -f docker-compose.pulsai.yaml up -d

# Stop all services
docker-compose -f docker-compose.pulsai.yaml down

# View logs
docker-compose -f docker-compose.pulsai.yaml logs -f

# View specific service logs
docker-compose -f docker-compose.pulsai.yaml logs -f pulsai-backend

# Restart a service
docker-compose -f docker-compose.pulsai.yaml restart pulsai-backend

# Rebuild and restart
docker-compose -f docker-compose.pulsai.yaml up -d --build

# Stop and remove volumes (⚠️ deletes data)
docker-compose -f docker-compose.pulsai.yaml down -v
```

### Scaling

```bash
# Scale backend (load balancing)
docker-compose -f docker-compose.pulsai.yaml up -d --scale pulsai-backend=3

# Note: Requires load balancer (nginx) configuration
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```ini
# Application
WEBUI_NAME=Pulsai
WEBUI_SECRET_KEY=your-super-secret-key-change-me

# Features
ENABLE_SIGNUP=true
ENABLE_WEBHOOKS=true
ANONYMIZED_TELEMETRY=false

# Database
DATABASE_URL=sqlite:///app/backend/data/webui.db

# Redis
REDIS_URL=redis://pulsai-redis:6379/0

# Ollama
OLLAMA_BASE_URL=http://pulsai-ollama:11434

# Logging
LOG_LEVEL=INFO
```

### MCP Configuration

Edit `config/mcp-servers.yaml`:

```yaml
servers:
  - id: "pulsai-stdio-mcp"
    name: "Pulsai Local Stdio MCP"
    protocol: "stdio"
    enabled: true
    config:
      command: ["python", "mcp-server/pulsai_mcp/server.py"]

  - id: "pulsai-http-mcp"
    name: "Pulsai HTTP MCP"
    protocol: "http"
    enabled: true
    config:
      url: "http://pulsai-mcp:8001"
```

### Volumes

Persistent data is stored in Docker volumes:

```bash
# List volumes
docker volume ls | grep pulsai

# Backup volume
docker run --rm -v pulsai-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/pulsai-data-backup.tar.gz -C /data .

# Restore volume
docker run --rm -v pulsai-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/pulsai-data-backup.tar.gz -C /data
```

**Volumes:**
- `pulsai-data`: Backend data (DB, uploads, models)
- `pulsai-redis-data`: Redis persistence
- `pulsai-ollama-data`: Ollama models

---

## 🎮 Usage Examples

### 1. Development Setup

```bash
# Use local code with hot reload
docker-compose -f docker-compose.pulsai.yaml up -d pulsai-redis pulsai-ollama pulsai-mcp

# Run backend locally
cd backend
pip install -r requirements.txt
bash start.sh
```

### 2. Production Deployment

```bash
# Build production images
./build-pulsai.sh --tag v1.0.0 --no-cache

# Tag for registry
docker tag pulsai/backend:v1.0.0 registry.example.com/pulsai/backend:v1.0.0
docker tag pulsai/mcp:v1.0.0 registry.example.com/pulsai/mcp:v1.0.0

# Push to registry
docker push registry.example.com/pulsai/backend:v1.0.0
docker push registry.example.com/pulsai/mcp:v1.0.0

# Deploy on server
docker-compose -f docker-compose.pulsai.yaml pull
docker-compose -f docker-compose.pulsai.yaml up -d
```

### 3. GPU Support (NVIDIA)

```bash
# Build with CUDA
./build-pulsai.sh --cuda

# Update docker-compose.pulsai.yaml
# Uncomment GPU sections for ollama service

# Start with GPU
docker-compose -f docker-compose.pulsai.yaml up -d
```

### 4. Custom Port Binding

Edit `docker-compose.pulsai.yaml`:

```yaml
services:
  pulsai-backend:
    ports:
      - "3000:8080"  # Custom port 3000
```

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose -f docker-compose.pulsai.yaml logs pulsai-backend

# Common issues:
# 1. Port 8080 already in use
docker ps | grep 8080
# Change port in docker-compose.pulsai.yaml

# 2. Database migration failed
docker-compose -f docker-compose.pulsai.yaml exec pulsai-backend \
  bash -c "cd /app/backend && alembic upgrade head"

# 3. Volume permissions
docker-compose -f docker-compose.pulsai.yaml down -v
docker volume rm pulsai-data
docker-compose -f docker-compose.pulsai.yaml up -d
```

### Ollama models not loading

```bash
# Check Ollama service
docker-compose -f docker-compose.pulsai.yaml logs pulsai-ollama

# Pull models manually
docker-compose -f docker-compose.pulsai.yaml exec pulsai-ollama \
  ollama pull llama2

# List models
docker-compose -f docker-compose.pulsai.yaml exec pulsai-ollama \
  ollama list
```

### Redis connection issues

```bash
# Test Redis
docker-compose -f docker-compose.pulsai.yaml exec pulsai-redis redis-cli ping
# Should return: PONG

# Check network
docker network inspect pulsai-network

# Restart Redis
docker-compose -f docker-compose.pulsai.yaml restart pulsai-redis
```

### MCP Server not responding

```bash
# Check health
curl http://localhost:8001/health

# View logs
docker-compose -f docker-compose.pulsai.yaml logs pulsai-mcp

# Restart MCP
docker-compose -f docker-compose.pulsai.yaml restart pulsai-mcp
```

### Out of disk space

```bash
# Clean up unused images
docker image prune -a

# Clean up volumes (⚠️ deletes data)
docker volume prune

# Clean build cache
docker builder prune

# Remove stopped containers
docker container prune
```

### High memory usage

```bash
# Check resource usage
docker stats

# Add memory limits in docker-compose.pulsai.yaml:
services:
  pulsai-backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 📊 Health Checks

All services have health checks:

```bash
# Backend
curl http://localhost:8080/health

# Redis
docker-compose -f docker-compose.pulsai.yaml exec pulsai-redis redis-cli ping

# MCP
curl http://localhost:8001/health

# Ollama
curl http://localhost:11434/api/version
```

---

## 🔐 Security

### Change default secrets

```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
WEBUI_SECRET_KEY=your-generated-secret-here
```

### Use HTTPS

Add nginx reverse proxy:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - pulsai-backend
```

### Network isolation

```yaml
networks:
  pulsai-network:
    driver: bridge
    internal: false
  pulsai-internal:
    driver: bridge
    internal: true  # No external access
```

---

## 📈 Monitoring

### Prometheus metrics

```bash
# Add to docker-compose.pulsai.yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### Log aggregation

```bash
# Use Docker logging driver
services:
  pulsai-backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🚀 Performance Tips

1. **Use build cache:**
   ```bash
   # Don't use --no-cache unless necessary
   ./build-pulsai.sh
   ```

2. **Multi-stage builds:**
   - Already optimized in Dockerfile
   - Reduces final image size by 50%

3. **Layer caching:**
   - Dependencies installed before code copy
   - Faster rebuilds on code changes

4. **Volume mounts for development:**
   ```yaml
   volumes:
     - ./backend:/app/backend  # Live code reload
   ```

5. **Resource limits:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 4G
       reservations:
         cpus: '1.0'
         memory: 2G
   ```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Pulsai MCP Guide](./docs/MCP_GUIDE.md)
- [Pulsai Deployment Guide](./docs/DEPLOYMENT.md)
- [Kubernetes Deployment](./kubernetes/README.md)

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Pulsai Docker System** 🐳

