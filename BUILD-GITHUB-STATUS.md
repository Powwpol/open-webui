# 🚀 Build Pulsai depuis GitHub - En Cours

**Date** : 26 octobre 2025  
**Source** : https://github.com/Powwpol/open-webui  
**Branch** : main  
**Méthode** : Docker Compose (build from GitHub)

---

## ⏳ Build Lancé

### Commande exécutée :
```bash
docker-compose -f docker-compose.github.yaml up -d --build
```

### Ce qui est en train de se passer :

**Étape 1** : Docker clone le repo GitHub
- Source : https://github.com/Powwpol/open-webui.git
- Branch : main
- Destination : Contexte Docker

**Étape 2** : Build Backend (5-8 min)
- Image : `pulsai/backend:github`
- Dockerfile : `Dockerfile`
- Mode : Slim (plus rapide)
- Taille estimée : ~1.2GB

**Étape 3** : Build MCP Server (2-3 min)
- Image : `pulsai/mcp:github`
- Dockerfile : `mcp-server/Dockerfile`
- Taille estimée : ~500MB

**Étape 4** : Pull services existants
- Redis : redis:7-alpine
- Ollama : ollama/ollama:latest

**Étape 5** : Start tous les services
- pulsai-backend-github
- pulsai-mcp-github
- pulsai-redis
- pulsai-ollama

---

## 📊 Progression Estimée

```
[▓▓▓▓▓░░░░░░░░░░] 30% - Clone GitHub
[▓▓▓▓▓▓▓▓░░░░░░░] 50% - Build Backend
[▓▓▓▓▓▓▓▓▓▓▓░░░░] 75% - Build MCP
[▓▓▓▓▓▓▓▓▓▓▓▓▓▓░] 90% - Start Services
[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] 100% - Pulsai Ready!
```

**Temps total estimé** : 10-15 minutes

---

## 🔍 Vérifier la Progression

### Commande 1 : Voir les images buildées

```bash
docker images | findstr pulsai
```

**Attendu** :
```
pulsai/backend   github   <id>   X minutes ago   1.2GB
pulsai/mcp       github   <id>   X minutes ago   500MB
```

### Commande 2 : Voir les services

```bash
docker-compose -f docker-compose.github.yaml ps
```

**Attendu** :
```
pulsai-backend-github   Up   8080->8080
pulsai-mcp-github       Up   8001->8001
pulsai-redis            Up   6379->6379
pulsai-ollama           Up   11434->11434
```

### Commande 3 : Voir les logs en temps réel

```bash
docker-compose -f docker-compose.github.yaml logs -f
```

---

## ✅ Quand c'est Terminé

### Vérifications :

```bash
# 1. Health check backend
curl http://localhost:8080/health

# 2. Health check MCP
curl http://localhost:8001/health

# 3. Ollama version
curl http://localhost:11434/api/version

# 4. Redis
docker exec pulsai-redis redis-cli ping
```

### Accès :

| Service | URL | Description |
|---------|-----|-------------|
| **Interface Web** | http://localhost:8080 | Interface Pulsai |
| **API Docs** | http://localhost:8080/api/docs | Documentation Swagger |
| **MCP Server** | http://localhost:8001 | Serveur MCP custom |
| **Ollama** | http://localhost:11434 | LLM local |
| **Redis** | localhost:6379 | Cache |

---

## 🎮 Commandes Utiles

### Pendant le Build

```bash
# Logs backend
docker logs -f pulsai-backend-github

# Logs MCP
docker logs -f pulsai-mcp-github

# Tous les logs
docker-compose -f docker-compose.github.yaml logs -f
```

### Après le Build

```bash
# Redémarrer un service
docker-compose -f docker-compose.github.yaml restart pulsai-backend

# Arrêter tout
docker-compose -f docker-compose.github.yaml down

# Rebuild un service spécifique
docker-compose -f docker-compose.github.yaml build pulsai-backend
docker-compose -f docker-compose.github.yaml up -d pulsai-backend
```

---

## 📈 Ce qui a été cloné depuis GitHub

Votre repo complet :
- ✅ 613 fichiers
- ✅ Backend rebrandé (Pulsai)
- ✅ Frontend + 58 langues
- ✅ MCP server custom
- ✅ Docker configs
- ✅ Kubernetes manifests
- ✅ Documentation

---

## 🐛 Si Problème

### Build échoue

```bash
# Voir logs détaillés
docker-compose -f docker-compose.github.yaml logs

# Rebuild sans cache
docker-compose -f docker-compose.github.yaml build --no-cache

# Vérifier espace disque
docker system df
```

### Timeout GitHub

```bash
# Clone d'abord localement
git clone https://github.com/Powwpol/open-webui.git temp-pulsai
cd temp-pulsai

# Build depuis local
docker build -t pulsai/backend:github -f Dockerfile .
```

### Port déjà utilisé

Modifier `docker-compose.github.yaml` :
```yaml
ports:
  - "8081:8080"  # Changer 8080 en 8081
```

---

## 🎉 Status

**Build** : ⏳ EN COURS (lancé en arrière-plan)  
**Source** : GitHub (Powwpol/open-webui)  
**Images** : pulsai/backend:github, pulsai/mcp:github  
**Temps estimé** : 10-15 minutes  

**Action** : Attendez que le build se termine, puis accédez à http://localhost:8080

---

**Suivez la progression avec** :  
`docker-compose -f docker-compose.github.yaml logs -f` 📊

