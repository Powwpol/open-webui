# 🚀 Pulsai

**Plateforme d'Assistant IA avec Support MCP Multi-Protocole**

> Basé sur [Open WebUI](https://github.com/open-webui/open-webui) v0.6.32  
> Usage interne - 4 utilisateurs (conforme licence Open WebUI clause 5.i)

---

## ✨ Fonctionnalités Principales

- 🤖 **Support Multi-Backend** : OpenAI, Ollama, Anthropic, Google, et plus
- 🔌 **Configuration MCP Complète** : HTTPS, npx, Docker, WebSocket, SSE
- 🎨 **Interface Moderne** : SvelteKit + FastAPI
- 🌐 **Multi-langue** : 58 langues supportées (dont Français)
- 🐳 **Docker Ready** : Déploiement containerisé
- 📊 **RAG Avancé** : Vector databases, embeddings, reranking
- 🔐 **Sécurisé** : OAuth, LDAP, OIDC, groupes utilisateurs

---

## 🚀 Démarrage Rapide

### Option 1 : Docker Compose (Recommandé)

```bash
# Cloner le repo
git clone https://github.com/VOTRE-USERNAME/pulsai.git
cd pulsai

# Démarrer tous les services
docker-compose -f docker-compose.pulsai.yaml up -d

# Accéder à Pulsai
open http://localhost:8080
```

### Option 2 : Build Local

```bash
# Build les images
./build-pulsai.sh --slim

# Démarrer
docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## 🔌 Configuration MCP

Pulsai supporte **5 protocoles MCP** configurables depuis l'interface :

### 1. HTTP/HTTPS 🌐
```yaml
protocol: http
config:
  url: https://api.example.com/mcp
  auth_type: bearer
  token: your-token
```

### 2. Standard I/O (npx) 🖥️
```yaml
protocol: stdio
config:
  command: ['npx', '-y', '@modelcontextprotocol/server-filesystem']
```

### 3. Docker Container 🐳
```yaml
protocol: docker
config:
  container_name: my-mcp-server
  port: 8100
```

### 4. WebSocket 🔌
```yaml
protocol: websocket
config:
  url: wss://api.example.com/mcp
```

### 5. Server-Sent Events 📡
```yaml
protocol: sse
config:
  url: https://api.example.com/events
```

**Configuration** : Admin Settings → MCP → Ajouter un serveur

---

## 📦 Architecture

```
┌─────────────────────────────────────────────────┐
│              Stack Pulsai                       │
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

### Services

- **Backend** : FastAPI (port 8080)
- **Redis** : Cache & sessions (port 6379)
- **Ollama** : LLM local (port 11434)
- **MCP Server** : Custom tools (port 8001)

---

## 🛠️ Installation

### Prérequis

- Docker Desktop (Windows/Mac) ou Docker Engine (Linux)
- 8GB RAM minimum
- 20GB espace disque

### Build

```bash
# Version complète
./build-pulsai.sh

# Version slim (sans embeddings, plus rapide)
./build-pulsai.sh --slim

# Avec GPU
./build-pulsai.sh --cuda

# Build local depuis fichiers
./build-local.sh --slim
```

### Configuration

Créer `.env` à la racine :

```ini
# Application
WEBUI_NAME=Pulsai
WEBUI_SECRET_KEY=votre-secret-key-ici
ENABLE_SIGNUP=true

# Database
DATABASE_URL=sqlite:///app/backend/data/webui.db

# Redis
REDIS_URL=redis://pulsai-redis:6379/0

# Ollama
OLLAMA_BASE_URL=http://pulsai-ollama:11434

# Logging
LOG_LEVEL=INFO
```

---

## 📖 Documentation

- [Guide Docker](./DOCKER_PULSAI.md)
- [Configuration MCP](./docs/MCP_GUIDE.md)
- [Setup Local](./LOCALDEVREADME.md)
- [Déploiement Production](./docs/DEPLOYMENT.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [Setup GitHub](./GITHUB-SETUP.md)

---

## 🔧 Développement

### Setup Développement

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sur Windows
pip install -r requirements.txt
bash start.sh

# Frontend
npm install
npm run dev
```

### Tests

```bash
# Backend
pytest

# Frontend
npm run test
```

---

## 🎨 Personnalisation

### Thème Pulsai

Couleurs principales définies dans `tailwind.config.js` :

```javascript
colors: {
  'pulsai-primary': '#FF6A00',
  'pulsai-info': '#3B82F6',
  'pulsai-success': '#10B981',
  'pulsai-accent': '#8B5CF6',
}
```

### Logo

Remplacer les fichiers dans `static/` :
- `favicon.ico`
- `favicon.png`
- `apple-touch-icon.png`
- `splash.png`
- `splash-dark.png`

---

## 🤝 Contribution

**Projet interne - 4 utilisateurs**

Pour contribuer :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add: Amazing Feature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est basé sur Open WebUI et respecte sa licence.

**Usage autorisé** : Déploiement privé <50 utilisateurs (clause 5.i)

Voir fichiers :
- [LICENSE](./LICENSE) - Licence Open WebUI originale
- [LICENSE_NOTICE](./LICENSE_NOTICE) - Notice multi-licence
- [CONTRIBUTOR_LICENSE_AGREEMENT](./CONTRIBUTOR_LICENSE_AGREEMENT) - CLA

---

## 🆘 Support

- 📚 [Documentation](./docs/)
- 🐛 [Issues](https://github.com/VOTRE-USERNAME/pulsai/issues)
- 💬 Équipe interne

---

## 📊 Statistiques Projet

- **Backend** : Python 3.11 + FastAPI
- **Frontend** : SvelteKit + TypeScript
- **Base** : Open WebUI v0.6.32
- **Rebranding** : 102 fichiers modifiés, ~822 occurrences
- **Langues** : 58 langues supportées
- **MCP** : 5 protocoles (HTTP, stdio, Docker, WebSocket, SSE)

---

## 🎯 Roadmap

- [ ] Ajouter logos Pulsai personnalisés
- [ ] Tests automatisés complets
- [ ] CI/CD GitHub Actions
- [ ] Documentation complète en français
- [ ] Intégrations MCP personnalisées

---

## ⭐ Remerciements

Basé sur le travail exceptionnel de l'équipe [Open WebUI](https://github.com/open-webui/open-webui)

---

**Pulsai** - Votre assistant IA, votre façon 🚀

