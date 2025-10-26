# ⚡ Pulsai Quick Start

**Get Pulsai running in 5 minutes**

---

## 🚀 Option 1: Docker (Recommandé)

### Windows

```cmd
REM 1. Fixer Docker si nécessaire
fix-docker-simple.bat

REM 2. Build version SLIM (rapide, 8-10 min)
build-pulsai.bat --slim

REM 3. Démarrer Pulsai
docker-compose -f docker-compose.pulsai.yaml up -d

REM 4. Accéder à l'interface
start http://localhost:8080
```

### Linux/macOS

```bash
# 1. Build
./build-pulsai.sh --slim

# 2. Start
docker-compose -f docker-compose.pulsai.yaml up -d

# 3. Access
open http://localhost:8080
```

### Ou en 1 commande :

```bash
# Linux/macOS
./start-pulsai.sh

# Windows
# Lancer manuellement (pas de start-pulsai.bat encore)
```

---

## 📦 Ce qui est inclus

**4 services Docker:**
- `pulsai-backend` - FastAPI (port 8080)
- `pulsai-redis` - Cache (port 6379)
- `pulsai-ollama` - LLM local (port 11434)
- `pulsai-mcp` - MCP server (port 8001)

---

## ⚙️ Configuration Rapide

### 1. Variables d'environnement

Créer `.env` (optionnel):
```ini
WEBUI_NAME=Pulsai
WEBUI_SECRET_KEY=change-me
ENABLE_SIGNUP=true
LOG_LEVEL=INFO
```

### 2. MCP Servers

Le fichier `config/mcp-servers.yaml` est créé automatiquement.

Pour le modifier:
```yaml
servers:
  - id: "pulsai-http-mcp"
    name: "Pulsai MCP"
    protocol: "http"
    enabled: true
    config:
      url: "http://pulsai-mcp:8001"
```

---

## 🎮 Commandes Utiles

```bash
# Voir les logs
docker-compose -f docker-compose.pulsai.yaml logs -f

# Arrêter
docker-compose -f docker-compose.pulsai.yaml down

# Redémarrer
docker-compose -f docker-compose.pulsai.yaml restart

# Santé des services
make health  # ou curl http://localhost:8080/health
```

---

## 🦙 Ajouter un modèle Ollama

```bash
# Lister les modèles disponibles
docker-compose -f docker-compose.pulsai.yaml exec pulsai-ollama ollama list

# Télécharger un modèle
docker-compose -f docker-compose.pulsai.yaml exec pulsai-ollama ollama pull llama2

# Ou avec make
make ollama-pull MODEL=llama2
```

**Modèles recommandés:**
- `llama2` (3.8GB) - Général
- `mistral` (4.1GB) - Rapide
- `phi3` (2.3GB) - Petit et efficace
- `codellama` (3.8GB) - Code

---

## 🔧 Résolution de Problèmes

### Docker ne démarre pas
```cmd
fix-docker-simple.bat
```

### Build échoue (Windows)
```cmd
REM Version SLIM = 2x plus rapide
build-pulsai.bat --slim

REM Si encore échec: clean build
build-pulsai.bat --slim --no-cache
```

### Port 8080 déjà utilisé

Éditer `docker-compose.pulsai.yaml`:
```yaml
services:
  pulsai-backend:
    ports:
      - "3000:8080"  # Utiliser port 3000
```

### Plus de problèmes ?
Voir [TROUBLESHOOTING-DOCKER.md](./TROUBLESHOOTING-DOCKER.md)

---

## 🎯 Premiers Pas

1. **Créer un compte:** http://localhost:8080
2. **Télécharger un modèle:** `make ollama-pull MODEL=llama2`
3. **Commencer à chatter !** 🎉

---

## 📊 Ressources

**Minimales (SLIM):**
- RAM: 4GB
- Disk: 10GB
- CPU: 2 cores

**Recommandées:**
- RAM: 8GB
- Disk: 20GB
- CPU: 4 cores

---

## 📚 Documentation Complète

- **Docker Guide:** [DOCKER_PULSAI.md](./DOCKER_PULSAI.md)
- **Docker Quick Ref:** [README-DOCKER.md](./README-DOCKER.md)
- **Troubleshooting:** [TROUBLESHOOTING-DOCKER.md](./TROUBLESHOOTING-DOCKER.md)
- **MCP Guide:** [docs/MCP_GUIDE.md](./docs/MCP_GUIDE.md)
- **API Docs:** http://localhost:8080/api/docs

---

## 💡 Tips

### Build plus rapide
```bash
# SLIM = sans embeddings models (2x faster)
build-pulsai.bat --slim
```

### Sauvegarde rapide
```bash
make backup
# Crée: backups/pulsai-data-20251019.tar.gz
```

### Mise à jour
```bash
git pull
make update  # Build + restart
```

---

## 🆘 Besoin d'Aide ?

1. **Check health:** `make health`
2. **View logs:** `make logs`
3. **Status:** `make status`
4. **Troubleshoot:** [TROUBLESHOOTING-DOCKER.md](./TROUBLESHOOTING-DOCKER.md)

---

**🚀 Pulsai - Next-Gen AI Assistant Platform**  
**Last Updated:** 19 octobre 2025





