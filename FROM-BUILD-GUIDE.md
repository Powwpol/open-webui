# 🔄 Transformation Build xn3xof → Pulsai Backend

## 📊 État Actuel du Projet

### ✅ Services Actifs
- **Ollama** : `pulsai-ollama` (port 11434) - ✅ Running
- **2 conteneurs Node.js** actifs

### 📦 Build Disponible
- **Image xn3xof** : `open-webui-open-webui:latest` 
  - Taille : 8.05 GB
  - Créé : 4 octobre 2025
  - **C'est votre build Pulsai complet**

### 💾 Volumes Existants
- `pulsai-data` - Données backend
- `pulsai-redis-data` - Cache Redis
- `pulsai-ollama-data` - Modèles Ollama
- `open-webui_open-webui-data` - Données du build original

### 🌐 Réseau
- `pulsai-network` - Réseau bridge configuré

---

## 🚀 Procédure d'Intégration

### Option 1 : Démarrage Rapide (Recommandé)

```cmd
REM 1. Transformer et démarrer en une seule commande
start-from-build.bat
```

**Cette commande va :**
1. ✅ Tag l'image `open-webui-open-webui:latest` → `pulsai/backend:from-build`
2. ✅ Nettoyer les conteneurs arrêtés
3. ✅ Connecter Ollama au réseau Pulsai
4. ✅ Démarrer Redis, Backend, MCP Server
5. ✅ Vérifier les health checks
6. ✅ Afficher le statut

---

### Option 2 : Étape par Étape

#### Étape 1 : Transformer l'Image

```cmd
transform-build-to-pulsai.bat
```

#### Étape 2 : Démarrer les Services

```cmd
docker-compose -f docker-compose.from-build.yaml up -d
```

#### Étape 3 : Vérifier les Logs

```cmd
docker-compose -f docker-compose.from-build.yaml logs -f
```

---

## 🌐 Accès aux Services

Une fois démarrés :

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8080 | API FastAPI + Interface Web |
| **API Docs** | http://localhost:8080/api/docs | Documentation Swagger |
| **MCP Server** | http://localhost:8001 | Serveur MCP custom |
| **Ollama** | http://localhost:11434 | LLM local |
| **Redis** | localhost:6379 | Cache |

---

## 🔍 Commandes Utiles

### Voir les Logs

```cmd
REM Tous les services
docker-compose -f docker-compose.from-build.yaml logs -f

REM Backend uniquement
docker-compose -f docker-compose.from-build.yaml logs -f pulsai-backend

REM MCP uniquement
docker-compose -f docker-compose.from-build.yaml logs -f pulsai-mcp
```

### Redémarrer un Service

```cmd
REM Redémarrer le backend
docker-compose -f docker-compose.from-build.yaml restart pulsai-backend

REM Redémarrer Redis
docker-compose -f docker-compose.from-build.yaml restart pulsai-redis
```

### Vérifier le Statut

```cmd
REM Statut des services
docker-compose -f docker-compose.from-build.yaml ps

REM Health checks
check-pulsai-status.bat
```

### Arrêter les Services

```cmd
REM Arrêter tout
docker-compose -f docker-compose.from-build.yaml down

REM Arrêter et supprimer les volumes (⚠️ supprime les données)
docker-compose -f docker-compose.from-build.yaml down -v
```

---

## 🐛 Troubleshooting

### Le Backend ne démarre pas

```cmd
REM Voir les logs détaillés
docker-compose -f docker-compose.from-build.yaml logs pulsai-backend

REM Vérifier les volumes
docker volume inspect pulsai-data

REM Redémarrer avec rebuild
docker-compose -f docker-compose.from-build.yaml up -d --force-recreate pulsai-backend
```

### Port 8080 déjà utilisé

Modifier `docker-compose.from-build.yaml` :
```yaml
ports:
  - "8081:8080"  # Utiliser 8081 au lieu de 8080
```

### Redis ne se connecte pas

```cmd
REM Vérifier Redis
docker-compose -f docker-compose.from-build.yaml exec pulsai-redis redis-cli ping

REM Restart Redis
docker-compose -f docker-compose.from-build.yaml restart pulsai-redis
```

### Ollama n'est pas accessible

```cmd
REM Vérifier qu'Ollama est sur le bon réseau
docker network connect pulsai-network pulsai-ollama

REM Tester Ollama
curl http://localhost:11434/api/version
```

---

## 📊 Comparaison Build Original vs Pulsai

| Aspect | Build xn3xof | Pulsai Stack |
|--------|-------------|--------------|
| **Image** | `open-webui-open-webui:latest` | `pulsai/backend:from-build` |
| **Taille** | 8.05 GB | 8.05 GB (même) |
| **Services** | Monolithique | Multi-services (Backend, Redis, MCP, Ollama) |
| **Réseau** | Standalone | `pulsai-network` |
| **Volumes** | `open-webui_open-webui-data` | `pulsai-data` (réutilisé) |
| **Configuration** | Standard Pulsai | Pulsai avec MCP |

---

## 💡 Avantages de l'Intégration

✅ **Réutilise votre build existant** - Pas besoin de rebuild  
✅ **Stack complète** - Backend + Redis + MCP + Ollama  
✅ **Configuration MCP** - Supporte les serveurs MCP customs  
✅ **Volumes persistants** - Données sauvegardées  
✅ **Réseau isolé** - Sécurité améliorée  
✅ **Health checks** - Monitoring automatique  

---

## 🎯 Next Steps

1. **Démarrer maintenant :**
   ```cmd
   start-from-build.bat
   ```

2. **Créer un compte admin :**
   - Aller sur http://localhost:8080
   - Créer votre premier compte (sera admin)

3. **Configurer MCP :**
   - Éditer `config/mcp-servers.yaml`
   - Activer les serveurs MCP souhaités

4. **Tester Ollama :**
   - Pull un modèle : `docker exec pulsai-ollama ollama pull llama2`
   - Lister les modèles : `docker exec pulsai-ollama ollama list`

---

## 📚 Documentation

- **Status Check** : `check-pulsai-status.bat`
- **Transform Build** : `transform-build-to-pulsai.bat`
- **Start Stack** : `start-from-build.bat`
- **Docker Compose** : `docker-compose.from-build.yaml`

---

**Créé le** : 26 octobre 2025  
**Build Source** : xn3xof (open-webui-open-webui:latest)  
**Destination** : Pulsai Backend Stack

