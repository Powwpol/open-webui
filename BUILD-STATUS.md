# 🚀 Pulsai Build Status

**Build lancé:** 19 octobre 2025

---

## ⏳ Build en cours

### 📦 Ce qui est en train d'être buildé :

1. **Backend (pulsai/backend:local)**
   - Source: Fichiers locaux (`backend/open_webui/`)
   - Mode: SLIM (sans embeddings)
   - Temps estimé: ~5-8 minutes
   - Taille: ~1.2GB

2. **Frontend (pulsai/frontend:local)**
   - Source: Fichiers locaux (`src/`, `static/`)
   - Build: SvelteKit + Pyodide
   - Temps estimé: ~3-4 minutes
   - Taille: ~100MB

3. **MCP Server (pulsai/mcp:local)**
   - Source: `mcp-server/`
   - Custom Pulsai MCP
   - Temps estimé: ~2-3 minutes
   - Taille: ~500MB

**Total temps build: ~10-15 minutes**

---

## 🔍 Vérifier la progression

### Commande 1: Voir les images buildées

```cmd
docker images | findstr pulsai
```

**Attendu:**
```
pulsai/backend    local    <id>    X minutes ago    1.2GB
pulsai/frontend   local    <id>    X minutes ago    100MB
pulsai/mcp        local    <id>    X minutes ago    500MB
```

### Commande 2: Voir les processus Docker

```cmd
docker ps -a
```

### Commande 3: Voir les logs de build

```cmd
REM Logs généraux
docker events --since 5m

REM Ou utiliser le script
check-build-progress.bat
```

---

## ✅ Quand le build est terminé

### Vérifier que tout est OK :

```cmd
REM 1. Voir les images
docker images | findstr pulsai.*local

REM 2. Vérifier les tailles
docker images | findstr pulsai
```

**Résultat attendu :**
```
pulsai/backend     local     <id>     X ago     1.2GB    ✅
pulsai/frontend    local     <id>     X ago     100MB    ✅
pulsai/mcp         local     <id>     X ago     500MB    ✅
```

---

## 🚀 Lancer Pulsai après le build

### Option 1: Docker Compose (Recommandé)

```cmd
REM Démarrer tous les services
docker-compose -f docker-compose.local-build.yaml up -d

REM Vérifier le statut
docker-compose -f docker-compose.local-build.yaml ps

REM Voir les logs
docker-compose -f docker-compose.local-build.yaml logs -f
```

### Option 2: Conteneurs individuels

```cmd
REM Backend seul
docker run -d -p 8080:8080 \
  -v pulsai-data:/app/backend/data \
  --name pulsai-backend-test \
  pulsai/backend:local

REM Frontend seul
docker run -d -p 3000:80 \
  --name pulsai-frontend-test \
  pulsai/frontend:local
```

---

## 🌐 Accès après démarrage

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface Pulsai (Nginx) |
| **Backend API** | http://localhost:8080 | API FastAPI |
| **API Docs** | http://localhost:8080/api/docs | Documentation Swagger |
| **MCP Server** | http://localhost:8001 | MCP Custom Server |
| **Ollama** | http://localhost:11434 | Ollama API |
| **Redis** | localhost:6379 | Cache Redis |

---

## 🔧 Troubleshooting

### Build échoue ?

```cmd
REM 1. Voir les logs
docker events --since 10m

REM 2. Nettoyer et réessayer
docker system prune -f
.\build-local.bat --slim --no-cache

REM 3. Vérifier l'espace disque
docker system df
```

### Build trop lent ?

**Solutions:**
1. ✅ Version SLIM déjà utilisée (pas d'embeddings)
2. ✅ Vérifier pas d'autres builds en cours: `docker ps`
3. ✅ Augmenter ressources WSL (voir `.wslconfig`)
4. ✅ Nettoyer cache: `docker builder prune`

### Erreurs I/O ?

```cmd
REM Fix Docker WSL
.\fix-docker-simple.bat

REM Puis rebuild
.\build-local.bat --slim
```

---

## 📊 Progression attendue

### Étape 1: Backend (5-8 min)
```
[1/2] Building backend...
 → Installing Python dependencies...     [███████░░░] 70%
 → Copying application code...           [██████████] 100%
 → Creating data directory...            [██████████] 100%
✅ Backend built successfully
```

### Étape 2: Frontend (3-4 min)
```
[2/2] Building frontend...
 → Installing Node dependencies...       [███████░░░] 70%
 → Fetching Pyodide packages...          [█████░░░░░] 50%
 → Building SvelteKit app...             [████░░░░░░] 40%
 → Copying to Nginx...                   [██████████] 100%
✅ Frontend built successfully
```

### Étape 3: MCP Server (2-3 min)
```
[3/3] Building MCP server...
 → Installing MCP dependencies...        [████████░░] 80%
 → Copying MCP tools...                  [██████████] 100%
✅ MCP server built successfully
```

---

## 🎉 Build Complet

Quand vous voyez :

```
==================================================
   ✅ Build Complete!
==================================================

Built images:
pulsai/backend     local
pulsai/frontend    local
pulsai/mcp         local

Next steps:
1. Start all services:
   docker-compose -f docker-compose.local-build.yaml up -d
```

**C'est prêt ! 🎉**

---

## 🆘 Besoin d'aide ?

- **Check progress:** `check-build-progress.bat`
- **Full logs:** `docker events --since 15m`
- **Troubleshooting:** [TROUBLESHOOTING-DOCKER.md](./TROUBLESHOOTING-DOCKER.md)
- **Local dev guide:** [LOCALDEVREADME.md](./LOCALDEVREADME.md)

---

**Build lancé avec:** `build-local.bat --slim`  
**Temps estimé:** 10-15 minutes  
**Status:** ⏳ En cours...



