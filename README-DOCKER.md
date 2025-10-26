# 🐳 Pulsai Docker - Quick Start

**5-minute setup to get Pulsai running with Docker**

---

## ⚡ Quick Start (3 Commands)

```bash
# 1. Build images
./build-pulsai.sh

# 2. Start services
docker-compose -f docker-compose.pulsai.yaml up -d

# 3. Access Pulsai
open http://localhost:8080
```

**Windows:**
```cmd
REM 1. Build images
build-pulsai.bat

REM 2. Start services
docker-compose -f docker-compose.pulsai.yaml up -d

REM 3. Access Pulsai
start http://localhost:8080
```

---

## 🚀 Even Faster (1 Command)

```bash
# Linux/macOS
./start-pulsai.sh

# This script will:
# ✓ Check prerequisites
# ✓ Build images if needed
# ✓ Create configuration
# ✓ Start all services
# ✓ Perform health checks
```

---

## 📦 What Gets Installed

**4 Docker containers:**

| Service | Port | Description |
|---------|------|-------------|
| **pulsai-backend** | 8080 | Main FastAPI application |
| **pulsai-redis** | 6379 | Cache & sessions |
| **pulsai-ollama** | 11434 | Local LLM inference |
| **pulsai-mcp** | 8001 | Custom MCP server |

**Total disk space:** ~3.5GB

---

## 🎯 Access Points

After starting:

- **Web UI:** http://localhost:8080
- **API Docs:** http://localhost:8080/api/docs
- **MCP Server:** http://localhost:8001
- **Ollama API:** http://localhost:11434

---

## 🛠️ Common Commands

```bash
# View logs
docker-compose -f docker-compose.pulsai.yaml logs -f

# Stop services
docker-compose -f docker-compose.pulsai.yaml down

# Restart
docker-compose -f docker-compose.pulsai.yaml restart

# Update
git pull && ./build-pulsai.sh && docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## 🎮 Makefile Commands

```bash
make build          # Build images
make up             # Start services
make down           # Stop services
make logs           # View logs
make health         # Health checks
make backup         # Backup data
make clean          # Remove containers
```

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose -f docker-compose.pulsai.yaml logs pulsai-backend

# Restart
docker-compose -f docker-compose.pulsai.yaml restart pulsai-backend
```

### Port 8080 already in use
Edit `docker-compose.pulsai.yaml`:
```yaml
services:
  pulsai-backend:
    ports:
      - "3000:8080"  # Use port 3000 instead
```

### Clean start (removes data ⚠️)
```bash
docker-compose -f docker-compose.pulsai.yaml down -v
docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## 📚 Full Documentation

- **Complete Docker Guide:** [DOCKER_PULSAI.md](./DOCKER_PULSAI.md)
- **MCP System:** [docs/MCP_GUIDE.md](./docs/MCP_GUIDE.md)
- **Deployment:** [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)
- **Kubernetes:** [kubernetes/README.md](./kubernetes/README.md)

---

## ⚙️ Configuration

### Environment Variables

Create `.env`:
```ini
WEBUI_NAME=Pulsai
WEBUI_SECRET_KEY=your-secret-key-here
ENABLE_SIGNUP=true
LOG_LEVEL=INFO
```

### MCP Servers

Edit `config/mcp-servers.yaml`:
```yaml
servers:
  - id: "pulsai-http-mcp"
    name: "Pulsai HTTP MCP"
    protocol: "http"
    enabled: true
    config:
      url: "http://pulsai-mcp:8001"
```

---

## 🚀 Production Deployment

```bash
# Build production images
./build-pulsai.sh --tag v1.0.0 --no-cache

# Start with production config
docker-compose -f docker-compose.production.yaml up -d

# Add HTTPS with nginx
# See docs/DEPLOYMENT.md for details
```

---

## 💾 Backup & Restore

```bash
# Backup
make backup
# Creates: backups/pulsai-data-20251019-143000.tar.gz

# Restore
make restore FILE=pulsai-data-20251019-143000.tar.gz
```

---

## 🎓 First Steps After Install

1. **Create account:** http://localhost:8080
2. **Pull Ollama model:**
   ```bash
   docker-compose -f docker-compose.pulsai.yaml exec pulsai-ollama ollama pull llama2
   ```
3. **Configure MCP servers:** Settings → MCP
4. **Start chatting!** 🎉

---

## ⚡ GPU Support

```bash
# Build with CUDA
./build-pulsai.sh --cuda

# Uncomment GPU section in docker-compose.pulsai.yaml
# Then start
docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## 🔍 Health Checks

```bash
# All services
make health

# Individual services
curl http://localhost:8080/health       # Backend
curl http://localhost:8001/health       # MCP
curl http://localhost:11434/api/version # Ollama
docker-compose -f docker-compose.pulsai.yaml exec pulsai-redis redis-cli ping # Redis
```

---

## 📊 Resource Usage

**Typical usage (idle):**
- CPU: ~5-10%
- RAM: ~1.5GB
- Disk: ~3.5GB

**With active LLM (Llama 2 7B):**
- CPU: ~50-80%
- RAM: ~4-6GB
- Disk: ~7GB

---

## 🆘 Need Help?

- **Documentation:** [DOCKER_PULSAI.md](./DOCKER_PULSAI.md)
- **Logs:** `docker-compose -f docker-compose.pulsai.yaml logs -f`
- **Status:** `docker-compose -f docker-compose.pulsai.yaml ps`
- **GitHub Issues:** [github.com/youruser/pulsai/issues](https://github.com/youruser/pulsai/issues)

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Pulsai Docker** 🐳🚀

