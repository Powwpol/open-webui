# 🚀 Pulsai

**Advanced AI Assistant with Multi-Backend Support**

A modernized, production-ready AI platform built on Open Web UI with enterprise features.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.production.yaml)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-326CE5.svg)](kubernetes/pulsai/)
[![API](https://img.shields.io/badge/API-v1-orange.svg)](docs/API_REFERENCE.md)

---

## ✨ Features

### Core Capabilities
- 🤖 **Multi-Backend Inference**: Ollama + vLLM with intelligent load balancing
- 🔌 **MCP System**: Flexible Model Context Protocols (stdio, HTTP, Docker, SSE, WebSocket)
- 🪝 **Webhooks**: Event-driven automation with n8n integration
- 🎨 **Modern UI**: ReactBits animations with Pulsai branding
- 🌍 **58 Languages**: Full internationalization support

### Infrastructure
- 🐳 **Production Docker**: Multi-service compose with health checks
- ☸️ **Kubernetes**: Complete manifests with HPA, network policies, TLS
- 📊 **Monitoring**: Health checks, metrics, uptime tracking
- 🔒 **Security**: HMAC signatures, network policies, secrets management

### Developer Experience
- 📚 **Comprehensive Docs**: API reference, deployment guides, migration tools
- 🔧 **Extensible**: Plugin-based MCP system for custom integrations
- 🧪 **Production-Ready**: Load balancing, failover, auto-scaling

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/pulsai/pulsai.git
cd pulsai

# Configure environment
cp env.production.template .env.production
# Edit .env.production with your settings

# Start Pulsai
docker-compose -f docker-compose.production.yaml up -d

# Access at http://localhost:3000
```

### Kubernetes

```bash
# Install prerequisites (cert-manager, ingress-nginx)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Deploy Pulsai
kubectl apply -k kubernetes/pulsai/

# Get external IP
kubectl get ingress -n pulsai
```

### Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn open_webui.main:app --reload

# Frontend
npm install
npm run dev
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│              Frontend (SvelteKit + Nginx)            │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│         Backend API (FastAPI) + Inference Router    │
│    (Load Balancing, Failover, Health Monitoring)    │
└─┬──────┬──────┬──────┬──────┬──────┬───────────────┘
  │      │      │      │      │      │
┌─▼─┐ ┌──▼─┐ ┌──▼─┐ ┌──▼──┐ ┌▼──┐ ┌▼──┐
│PG │ │Redis│ │Ollama│ │vLLM │ │MCP│ │n8n│
└───┘ └────┘ └─────┘ └─────┘ └───┘ └───┘
```

---

## 🎯 Key Differences from Open Web UI

| Feature | Open Web UI | Pulsai |
|---------|-------------|---------|
| **Inference** | Ollama only | Ollama + vLLM + Load Balancing |
| **MCP Support** | Basic | 5 protocols + custom servers |
| **Webhooks** | None | Full n8n integration with retry |
| **Kubernetes** | Basic | Production manifests + HPA |
| **UI** | Standard | ReactBits animations + branding |
| **Translations** | Standard | Renamed UI elements (Functions→Outils) |
| **Documentation** | Good | Comprehensive (6 guides, 2000+ lines) |

**Backward Compatible:** 100% data migration from Open Web UI.

---

## 📖 Documentation

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Docker & Kubernetes deployment
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Migrate from Open Web UI
- **[MCP Guide](docs/MCP_GUIDE.md)** - Model Context Protocols setup
- **[vLLM Integration](docs/VLLM_INTEGRATION.md)** - High-performance inference
- **[n8n Integration](docs/N8N_INTEGRATION.md)** - Webhook automation
- **[Branding Guide](static/BRANDING.md)** - Visual identity & design system

---

## 🛠️ Configuration

### Environment Variables

Key configuration options in `.env.production`:

```bash
# Application
PULSAI_NAME=Pulsai
SECRET_KEY=your-secret-key

# Database
POSTGRES_PASSWORD=your-postgres-password
DATABASE_URL=postgresql://pulsai:password@postgres:5432/pulsai

# Inference Backends
OLLAMA_BASE_URL=http://ollama:11434
VLLM_ENABLED=true
VLLM_BASE_URL=http://vllm:8000

# MCP Configuration
MCP_CONFIG_PATH=/app/config/mcp-servers.yaml

# External APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Webhooks
N8N_WEBHOOK_URL=http://n8n:5678/webhook/pulsai
```

### MCP Configuration

Create `config/mcp-servers.yaml`:

```yaml
servers:
  - id: "pulsai-mcp"
    name: "Pulsai Custom MCP"
    protocol: "stdio"
    enabled: true
    config:
      command: ["python", "mcp-server/pulsai_mcp/server.py"]
  
  - id: "http-mcp"
    name: "HTTP MCP Server"
    protocol: "http"
    enabled: true
    config:
      url: "http://localhost:8100"
```

---

## 🔌 API Usage

### Generate Completion

```bash
curl -X POST http://localhost:8080/api/v1/inference/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "backend": "ollama"
  }'
```

### Create Webhook

```bash
curl -X POST http://localhost:8080/api/v1/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "n8n Integration",
    "url": "http://n8n:5678/webhook/pulsai",
    "event_types": ["chat.created", "chat.completed"]
  }'
```

### Add MCP Server

```bash
curl -X POST http://localhost:8080/api/v1/mcp/servers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "custom-mcp",
    "name": "Custom MCP",
    "protocol": "http",
    "enabled": true,
    "config": {"url": "http://localhost:8100"}
  }'
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
npm run test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e
```

---

## 📦 Project Structure

```
pulsai/
├── backend/
│   ├── open_webui/
│   │   ├── inference/          # vLLM + Ollama abstraction
│   │   ├── mcp/                # MCP protocol system
│   │   ├── webhooks/           # n8n integration
│   │   └── routers/            # API endpoints
│   └── requirements.txt
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   └── admin/Settings/
│   │   │       ├── MCP/        # MCP configuration UI
│   │   │       └── Inference/  # vLLM configuration UI
│   │   ├── reactbits/          # UI animations
│   │   └── i18n/locales/       # 58 language files
│   └── app.css                 # Pulsai branding
├── mcp-server/                 # Custom Pulsai MCP
├── kubernetes/pulsai/          # K8s manifests
├── docs/                       # Documentation (6 guides)
├── docker-compose.production.yaml
└── README.md
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/pulsai.git
cd pulsai

# Create branch
git checkout -b feature/amazing-feature

# Make changes
# ...

# Test
npm run test
pytest

# Commit
git commit -m "feat: add amazing feature"

# Push
git push origin feature/amazing-feature
```

---

## 📈 Roadmap

### v1.1 (Q1 2026)
- [ ] Recursive chat system with tree structure
- [ ] Auto fine-tuning pipeline
- [ ] Interaction quality scoring
- [ ] Non-uniform UI layouts

### v1.2 (Q2 2026)
- [ ] Multi-GPU support for vLLM
- [ ] Advanced analytics dashboard
- [ ] Custom model marketplace
- [ ] Mobile app (React Native)

### v2.0 (Q3 2026)
- [ ] Distributed inference across nodes
- [ ] Advanced RAG with hybrid search
- [ ] Voice interface
- [ ] Plugin marketplace

---

## 🔒 Security

- **HMAC Signatures**: All webhooks signed with SHA-256
- **Network Policies**: Kubernetes micro-segmentation
- **Secrets Management**: External secrets operator support
- **Rate Limiting**: 100 req/min per user
- **Input Validation**: Pydantic models throughout

**Report vulnerabilities**: security@pulsai.com

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Open Web UI** - Original project foundation
- **vLLM Team** - High-performance inference engine
- **Ollama** - Local model management
- **n8n** - Workflow automation
- **ReactBits** - UI component inspiration

---

## 📞 Support

- **Documentation**: https://docs.pulsai.com
- **GitHub Issues**: Bug reports and feature requests
- **Email**: support@pulsai.com
- **Enterprise**: enterprise@pulsai.com

---

## ⭐ Show Your Support

If Pulsai helps your project, please consider:
- ⭐ Star this repository
- 🐛 Report bugs
- 💡 Suggest features
- 📖 Improve documentation
- 🤝 Contribute code

---

**Built with ❤️ by the Pulsai Team**

**Version:** 1.0.0  
**Last Updated:** 19 octobre 2025
