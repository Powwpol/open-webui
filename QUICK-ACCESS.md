# 🚀 Pulsai - Accès Rapide

**Build xn3xof transformé et déployé avec succès !**

---

## 🌐 URLs

| Service | URL | Description |
|---------|-----|-------------|
| **🌐 Interface Web** | http://localhost:8080 | Interface principale Pulsai |
| **📚 API Docs** | http://localhost:8080/api/docs | Documentation Swagger |
| **🔌 MCP Server** | http://localhost:8001 | Serveur MCP custom |
| **🦙 Ollama** | http://localhost:11434 | API Ollama locale |

---

## ⚡ Commandes Rapides

### Démarrage / Arrêt

```cmd
REM Démarrer tout
docker-compose -f docker-compose.from-build.yaml up -d

REM Arrêter tout
docker-compose -f docker-compose.from-build.yaml down

REM Redémarrer
docker-compose -f docker-compose.from-build.yaml restart

REM Status
docker-compose -f docker-compose.from-build.yaml ps
```

### Logs

```cmd
REM Tous les logs (temps réel)
docker-compose -f docker-compose.from-build.yaml logs -f

REM Backend uniquement
docker logs -f pulsai-backend-from-build

REM MCP uniquement
docker logs -f pulsai-mcp
```

### Ollama

```cmd
REM Lister modèles
docker exec pulsai-ollama ollama list

REM Pull un modèle
docker exec pulsai-ollama ollama pull llama2

REM Run un modèle (test)
docker exec -it pulsai-ollama ollama run llama2
```

### Diagnostic

```cmd
REM Health checks
curl http://localhost:8080/health
curl http://localhost:8001/health
curl http://localhost:11434/api/version

REM Ressources
docker stats

REM Inspection
docker inspect pulsai-backend-from-build
```

---

## 🎯 Premier Accès

### 1. Ouvrir l'Interface

```cmd
start http://localhost:8080
```

Ou simplement cliquer : [http://localhost:8080](http://localhost:8080)

### 2. Créer un Compte Admin

- Email : votre@email.com
- Nom : Votre Nom
- Mot de passe : (sécurisé)

Le premier compte créé est automatiquement **admin**.

### 3. Configurer un Modèle

**Option A - Ollama Local** :
1. Admin Settings → Connections → Ollama
2. URL: `http://pulsai-ollama:11434`
3. Tester la connexion
4. Pull un modèle dans l'interface

**Option B - OpenAI** :
1. Settings → Connections → OpenAI
2. API Key : `sk-...`
3. Sauvegarder

### 4. Premier Chat

1. Cliquer "New Chat"
2. Sélectionner un modèle
3. Commencer à discuter !

---

## 🔧 Configuration MCP (Optionnel)

Éditer `config/mcp-servers.yaml` :

```yaml
mcp_servers:
  - id: "pulsai-custom"
    name: "Pulsai Custom MCP"
    protocol: "http"
    enabled: true
    config:
      url: "http://pulsai-mcp:8001"
      timeout: 60
```

Puis redémarrer :
```cmd
docker-compose -f docker-compose.from-build.yaml restart pulsai-backend
```

---

## 📊 État Actuel

```
✅ Backend:     http://localhost:8080 (Healthy)
✅ Frontend:    Intégré dans backend (200 OK)
✅ API:         http://localhost:8080/api/docs
✅ MCP:         http://localhost:8001
✅ Redis:       PONG
✅ Ollama:      v0.12.3

💾 Data:        ./pulsai-backend-data/
🌐 Network:     pulsai-network
📦 Image:       pulsai/backend:from-build (8.05GB)
```

---

## 🎉 Success!

Votre build **xn3xof** est maintenant transformé et déployé comme **stack Pulsai complète**.

**Tout est opérationnel et prêt à l'emploi !**

---

**Créé le** : 26 octobre 2025  
**Build** : xn3xof → Pulsai  
**Status** : 🟢 OPERATIONAL

