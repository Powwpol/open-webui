# Pulsai - Deployment Guide

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Security](#security)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Linux (Ubuntu 22.04+, Debian 12+), macOS, Windows with WSL2

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 100+ GB NVMe SSD
- GPU: NVIDIA GPU for local inference (optional)

### Software Dependencies

- **Docker:** 24.0+ with Docker Compose 2.20+
- **Kubernetes:** 1.28+ (for K8s deployment)
- **kubectl:** Latest version
- **Git:** For cloning repository

---

## 🐳 Docker Compose Deployment

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/pulsai/pulsai.git
cd pulsai

# 2. Create environment file
cp env.production.template .env.production

# 3. Edit configuration
nano .env.production  # Update passwords, API keys, etc.

# 4. Start services
docker-compose -f docker-compose.production.yaml up -d

# 5. Check status
docker-compose -f docker-compose.production.yaml ps

# 6. View logs
docker-compose -f docker-compose.production.yaml logs -f pulsai-backend
```

### Initial Setup

```bash
# Initialize database
docker-compose -f docker-compose.production.yaml exec pulsai-backend \
  python -m alembic upgrade head

# Create admin user
docker-compose -f docker-compose.production.yaml exec pulsai-backend \
  python -m open_webui.cli create-admin \
  --email admin@example.com \
  --password your-admin-password

# Download Ollama models (optional)
docker-compose -f docker-compose.production.yaml exec ollama \
  ollama pull llama2
```

### Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Nginx + SvelteKit)  :3000                   │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  Backend API (FastAPI)  :8080                          │
└─────┬────┬────┬────┬────┬────┬─────────────────────────┘
      │    │    │    │    │    │
      ▼    ▼    ▼    ▼    ▼    ▼
    ┌───┬───┬───┬───┬───┬───┐
    │PG │Redis│Ollama│Chroma│MCP│n8n│
    └───┴───┴───┴───┴───┴───┘
```

### Service Management

```bash
# Stop all services
docker-compose -f docker-compose.production.yaml down

# Stop without removing volumes (preserves data)
docker-compose -f docker-compose.production.yaml stop

# Restart specific service
docker-compose -f docker-compose.production.yaml restart pulsai-backend

# Scale backend
docker-compose -f docker-compose.production.yaml up -d --scale pulsai-backend=3

# Update images
docker-compose -f docker-compose.production.yaml pull
docker-compose -f docker-compose.production.yaml up -d

# Clean up
docker-compose -f docker-compose.production.yaml down -v  # WARNING: Deletes data!
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify connection to cluster
kubectl cluster-info
kubectl get nodes
```

### Deploy to Kubernetes

```bash
# 1. Create namespace
kubectl create namespace pulsai

# 2. Create secrets
kubectl create secret generic pulsai-secrets \
  --from-literal=postgres-password=your-postgres-password \
  --from-literal=secret-key=your-secret-key \
  --namespace=pulsai

# 3. Apply configurations
kubectl apply -f kubernetes/pulsai/ --namespace=pulsai

# 4. Check deployment status
kubectl get pods -n pulsai
kubectl get services -n pulsai

# 5. Get external IP
kubectl get ingress -n pulsai
```

### Scale Deployment

```bash
# Scale backend pods
kubectl scale deployment pulsai-backend --replicas=5 -n pulsai

# Autoscaling
kubectl autoscale deployment pulsai-backend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n pulsai
```

---

## ⚙️ Configuration

### Environment Variables

Key environment variables to configure:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Application secret key | - | ✅ |
| `POSTGRES_PASSWORD` | Database password | - | ✅ |
| `OPENAI_API_KEY` | OpenAI API key | - | ❌ |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | ❌ |
| `PULSAI_PORT` | Frontend port | 3000 | ❌ |
| `PULSAI_API_PORT` | Backend API port | 8080 | ❌ |

### MCP Configuration

Create `config/mcp-servers.yaml`:

```yaml
servers:
  - id: "pulsai-stdio-mcp"
    name: "Pulsai Local MCP"
    protocol: "stdio"
    enabled: true
    config:
      command: ["python", "mcp-server/pulsai_mcp/server.py"]
  
  - id: "example-http-mcp"
    name: "HTTP MCP Server"
    protocol: "http"
    enabled: false
    config:
      url: "http://localhost:8100"
```

---

## 🔒 Security

### SSL/TLS Configuration

**Using Let's Encrypt with Docker:**

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Using Kubernetes Ingress:**

```yaml
# kubernetes/pulsai/ingress/pulsai-ingress.yaml
spec:
  tls:
    - hosts:
        - your-domain.com
      secretName: pulsai-tls
```

### Firewall Rules

```bash
# Allow necessary ports only
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Secrets Management

**Docker Secrets:**
```bash
# Create secret
echo "my-secret-key" | docker secret create pulsai-secret-key -

# Use in compose
services:
  pulsai-backend:
    secrets:
      - pulsai-secret-key
```

**Kubernetes Secrets:**
```bash
# Create from file
kubectl create secret generic pulsai-config \
  --from-file=mcp-servers.yaml=config/mcp-servers.yaml \
  -n pulsai

# Use external secrets operator
kubectl apply -f https://raw.githubusercontent.com/external-secrets/external-secrets/main/deploy/crds/bundle.yaml
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8080/health

# Frontend health
curl http://localhost:3000/health

# Check all services
docker-compose -f docker-compose.production.yaml ps
```

### Logs

```bash
# Follow all logs
docker-compose -f docker-compose.production.yaml logs -f

# Specific service
docker-compose -f docker-compose.production.yaml logs -f pulsai-backend

# Last 100 lines
docker-compose -f docker-compose.production.yaml logs --tail=100 pulsai-backend

# Kubernetes logs
kubectl logs -f deployment/pulsai-backend -n pulsai
```

### Metrics (Prometheus + Grafana)

```bash
# Add to docker-compose.production.yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
```

---

## 💾 Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.production.yaml exec postgres \
  pg_dump -U pulsai pulsai > backup-$(date +%Y%m%d).sql

# Restore
docker-compose -f docker-compose.production.yaml exec -T postgres \
  psql -U pulsai pulsai < backup-20250119.sql
```

### Volume Backup

```bash
# Backup all volumes
docker run --rm \
  -v pulsai_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-data-$(date +%Y%m%d).tar.gz /data

# Restore
docker run --rm \
  -v pulsai_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/postgres-data-20250119.tar.gz -C /
```

### Automated Backups

```bash
# Cron job (daily at 2 AM)
0 2 * * * /path/to/pulsai/scripts/backup.sh
```

---

## 🔧 Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check logs
docker-compose -f docker-compose.production.yaml logs pulsai-backend

# Common fixes:
# 1. Database not ready
docker-compose -f docker-compose.production.yaml up -d postgres
sleep 30
docker-compose -f docker-compose.production.yaml up -d pulsai-backend

# 2. Port already in use
sudo lsof -i :8080
# Kill process or change PULSAI_API_PORT
```

#### Database Connection Failed

```bash
# Test PostgreSQL connection
docker-compose -f docker-compose.production.yaml exec postgres \
  psql -U pulsai -d pulsai -c "SELECT 1;"

# Reset database (WARNING: Data loss!)
docker-compose -f docker-compose.production.yaml down -v
docker-compose -f docker-compose.production.yaml up -d
```

#### Out of Memory

```bash
# Check memory usage
docker stats

# Increase limits in docker-compose.production.yaml
deploy:
  resources:
    limits:
      memory: 8G
```

#### Slow Performance

```bash
# Check resource usage
docker stats

# Optimize PostgreSQL
# Add to docker-compose.production.yaml:
command: >
  postgres
  -c shared_buffers=512MB
  -c max_connections=200
```

### Debug Mode

```bash
# Enable debug logging
echo "DEBUG=true" >> .env.production

# Restart backend
docker-compose -f docker-compose.production.yaml restart pulsai-backend

# Check detailed logs
docker-compose -f docker-compose.production.yaml logs -f --tail=1000 pulsai-backend
```

---

## 🚀 Production Checklist

- [ ] Update `env.production.template` → `.env.production`
- [ ] Generate strong `SECRET_KEY` and `POSTGRES_PASSWORD`
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Configure MCP servers in `config/mcp-servers.yaml`
- [ ] Enable automated backups
- [ ] Set up monitoring and alerting
- [ ] Test health check endpoints
- [ ] Configure log rotation
- [ ] Set up CDN for static assets (optional)
- [ ] Configure rate limiting
- [ ] Test disaster recovery procedures

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Maintainer:** Pulsai Team

