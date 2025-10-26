# 🏗️ Pulsai Local Development Build

**Build frontend et backend depuis vos fichiers locaux**

---

## 🎯 Vue d'Ensemble

Ce guide permet de builder et déployer Pulsai en utilisant vos fichiers sources locaux, parfait pour :
- ✅ Développement local
- ✅ Tests de modifications
- ✅ Debug
- ✅ Contributions

---

## 🚀 Quick Start

### Option 1: Script Automatique (Recommandé)

**Windows:**
```cmd
REM Build tout (backend + frontend + MCP)
build-local.bat

REM Build version slim (plus rapide)
build-local.bat --slim

REM Build sans cache
build-local.bat --no-cache --slim
```

**Linux/macOS:**
```bash
# Build tout
./build-local.sh

# Build version slim
./build-local.sh --slim

# Build sans cache
./build-local.sh --no-cache --slim
```

### Option 2: Docker Compose Direct

```bash
# Build et start en une commande
docker-compose -f docker-compose.local-build.yaml up -d --build

# Rebuild spécifique
docker-compose -f docker-compose.local-build.yaml build pulsai-backend
docker-compose -f docker-compose.local-build.yaml build pulsai-frontend

# Start sans rebuild
docker-compose -f docker-compose.local-build.yaml up -d
```

---

## 📦 Structure Build

### Backend (`docker/pulsai-backend.Dockerfile`)

**Build depuis:**
```
✅ backend/requirements.txt      → Dépendances Python
✅ backend/open_webui/           → Code application
✅ backend/migrations/           → Migrations DB
✅ backend/alembic.ini           → Config Alembic
✅ backend/start.sh              → Script démarrage
✅ config/                       → Configuration MCP
```

**Résultat:**
- Image: `pulsai/backend:local`
- Port: `8080`
- Taille: ~1.2GB (slim) / ~2.5GB (full)

### Frontend (`docker/pulsai-frontend.Dockerfile`)

**Build depuis:**
```
✅ package.json, package-lock.json → Dépendances Node
✅ src/                            → Code Svelte
✅ static/                         → Assets statiques
✅ scripts/prepare-pyodide.js      → Pyodide setup
✅ svelte.config.js                → Config Svelte
✅ vite.config.ts                  → Config Vite
✅ tailwind.config.js              → Config Tailwind
✅ tsconfig.json                   → Config TypeScript
```

**Résultat:**
- Image: `pulsai/frontend:local`
- Port: `80` (mappé sur `3000`)
- Taille: ~100MB
- Serveur: Nginx

### MCP Server (`mcp-server/Dockerfile`)

**Build depuis:**
```
✅ mcp-server/pyproject.toml  → Dépendances
✅ mcp-server/pulsai_mcp/     → Code MCP server
```

**Résultat:**
- Image: `pulsai/mcp:local`
- Port: `8001`
- Taille: ~500MB

---

## 🔧 Configuration

### Variables d'Environnement

Créer `.env` à la racine:
```ini
# Pulsai Core
WEBUI_NAME=Pulsai
WEBUI_SECRET_KEY=your-super-secret-key-change-me
ENABLE_SIGNUP=true

# Logging
LOG_LEVEL=DEBUG  # Pour dev: DEBUG, INFO, WARNING, ERROR

# Ollama
OLLAMA_BASE_URL=http://pulsai-ollama:11434

# Redis
REDIS_URL=redis://pulsai-redis:6379/0
```

### MCP Configuration

Éditer `config/mcp-servers.yaml`:
```yaml
servers:
  - id: "pulsai-http-mcp"
    name: "Pulsai Local MCP"
    protocol: "http"
    enabled: true
    config:
      url: "http://pulsai-mcp:8001"
```

---

## 🎮 Commandes

### Build

```bash
# Build tout
./build-local.sh

# Build backend uniquement
docker build -t pulsai/backend:local -f docker/pulsai-backend.Dockerfile .

# Build frontend uniquement
docker build -t pulsai/frontend:local -f docker/pulsai-frontend.Dockerfile .

# Build avec variables
docker build \
  --build-arg USE_SLIM=true \
  -t pulsai/backend:local-slim \
  -f docker/pulsai-backend.Dockerfile \
  .
```

### Start/Stop

```bash
# Start tous les services
docker-compose -f docker-compose.local-build.yaml up -d

# Stop
docker-compose -f docker-compose.local-build.yaml down

# Restart un service
docker-compose -f docker-compose.local-build.yaml restart pulsai-backend

# Voir les logs
docker-compose -f docker-compose.local-build.yaml logs -f

# Logs d'un service
docker-compose -f docker-compose.local-build.yaml logs -f pulsai-backend
```

### Dev Workflow

```bash
# 1. Modifier le code
nano src/lib/components/...

# 2. Rebuild le service modifié
docker-compose -f docker-compose.local-build.yaml build pulsai-frontend

# 3. Restart le service
docker-compose -f docker-compose.local-build.yaml up -d pulsai-frontend

# 4. Voir les logs
docker-compose -f docker-compose.local-build.yaml logs -f pulsai-frontend
```

---

## 🐛 Debug

### Entrer dans un container

```bash
# Backend
docker-compose -f docker-compose.local-build.yaml exec pulsai-backend bash

# Frontend (Nginx)
docker-compose -f docker-compose.local-build.yaml exec pulsai-frontend sh

# MCP
docker-compose -f docker-compose.local-build.yaml exec pulsai-mcp bash
```

### Vérifier les fichiers buildés

```bash
# Backend
docker run --rm pulsai/backend:local ls -la /app/backend/open_webui

# Frontend
docker run --rm pulsai/frontend:local ls -la /usr/share/nginx/html
```

### Logs en temps réel

```bash
# Tous les services
docker-compose -f docker-compose.local-build.yaml logs -f --tail=100

# Un service spécifique
docker-compose -f docker-compose.local-build.yaml logs -f --tail=50 pulsai-backend
```

---

## 🔍 Troubleshooting

### Build échoue

**Backend:**
```bash
# Vérifier requirements.txt
cat backend/requirements.txt

# Build avec logs détaillés
docker build --no-cache --progress=plain \
  -t pulsai/backend:local \
  -f docker/pulsai-backend.Dockerfile \
  . 2>&1 | tee build.log
```

**Frontend:**
```bash
# Vérifier dépendances Node
npm ls

# Build avec logs
docker build --no-cache --progress=plain \
  -t pulsai/frontend:local \
  -f docker/pulsai-frontend.Dockerfile \
  . 2>&1 | tee build-frontend.log
```

### Container ne démarre pas

```bash
# Voir pourquoi
docker-compose -f docker-compose.local-build.yaml ps
docker-compose -f docker-compose.local-build.yaml logs pulsai-backend

# Recréer le container
docker-compose -f docker-compose.local-build.yaml up -d --force-recreate pulsai-backend
```

### Port déjà utilisé

```bash
# Changer le port dans docker-compose.local-build.yaml
services:
  pulsai-frontend:
    ports:
      - "3001:80"  # Au lieu de 3000
```

### Manque d'espace disque

```bash
# Nettoyer images inutilisées
docker system prune -a

# Nettoyer volumes
docker volume prune

# Voir l'espace
docker system df
```

---

## 📊 Différences Local vs Production

| Aspect | Local Build | Production Build |
|--------|-------------|------------------|
| **Images** | `pulsai/*:local` | `pulsai/*:latest` |
| **Source** | Fichiers locaux | Git/Registry |
| **Ports** | Frontend: 3000, Backend: 8080 | Nginx reverse proxy |
| **Volumes** | `-local` suffix | Standard |
| **Logs** | DEBUG | INFO/WARNING |
| **Hot Reload** | Non (rebuild) | N/A |
| **Taille** | Plus gros (layers dev) | Optimisé |

---

## 🎯 Workflow Développement

### 1. Setup Initial

```bash
# Clone repo (si pas déjà fait)
git clone https://github.com/youruser/pulsai.git
cd pulsai

# Build initial
./build-local.sh --slim

# Start
docker-compose -f docker-compose.local-build.yaml up -d

# Vérifier
curl http://localhost:8080/health
curl http://localhost:3000/health
```

### 2. Développer Backend

```bash
# 1. Modifier code Python
nano backend/open_webui/routers/...

# 2. Rebuild backend
docker-compose -f docker-compose.local-build.yaml build pulsai-backend

# 3. Restart
docker-compose -f docker-compose.local-build.yaml up -d pulsai-backend

# 4. Tester
curl http://localhost:8080/api/...
```

### 3. Développer Frontend

```bash
# 1. Modifier code Svelte
nano src/lib/components/...

# 2. Rebuild frontend
docker-compose -f docker-compose.local-build.yaml build pulsai-frontend

# 3. Restart
docker-compose -f docker-compose.local-build.yaml up -d pulsai-frontend

# 4. Tester dans navigateur
open http://localhost:3000
```

### 4. Tester MCP

```bash
# 1. Modifier MCP server
nano mcp-server/pulsai_mcp/...

# 2. Rebuild MCP
docker-compose -f docker-compose.local-build.yaml build pulsai-mcp

# 3. Restart
docker-compose -f docker-compose.local-build.yaml up -d pulsai-mcp

# 4. Tester
curl http://localhost:8001/health
curl http://localhost:8001/tools
```

---

## 🚀 Migration vers Production

Quand vous êtes prêt:

```bash
# 1. Stop local
docker-compose -f docker-compose.local-build.yaml down

# 2. Build production
./build-pulsai.sh --tag v1.0.0

# 3. Start production
docker-compose -f docker-compose.pulsai.yaml up -d

# 4. Ou push vers registry
docker push yourregistry/pulsai/backend:v1.0.0
docker push yourregistry/pulsai/frontend:v1.0.0
```

---

## 📚 Ressources

- **Docker Guide:** [DOCKER_PULSAI.md](./DOCKER_PULSAI.md)
- **Troubleshooting:** [TROUBLESHOOTING-DOCKER.md](./TROUBLESHOOTING-DOCKER.md)
- **Quick Start:** [QUICK-START.md](./QUICK-START.md)
- **MCP Guide:** [docs/MCP_GUIDE.md](./docs/MCP_GUIDE.md)

---

**Happy Local Development! 🎉**  
**Last Updated:** 19 octobre 2025



