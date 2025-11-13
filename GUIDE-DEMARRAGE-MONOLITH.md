# 🚀 Guide de Démarrage Rapide - PulsAI Monolithe

## ✅ Problème Résolu

Le problème `ModuleNotFoundError: No module named 'open_webui'` a été identifié et corrigé !

### Cause
Le fichier `backend/start.sh` utilisait encore l'ancien nom de module `open_webui` au lieu de `pulsai`.

### Solution Appliquée
✅ Fichier `backend/start.sh` corrigé : `pulsai.main:app` au lieu de `open_webui.main:app`

---

## 📋 Étapes pour Lancer PulsAI Monolithe

### Étape 1 : Build de l'Image (EN COURS)

Le build de la nouvelle image est en cours d'exécution :

```bash
build-monolith.bat --no-cache
```

**Temps estimé** : 10-15 minutes  
**Taille de l'image** : ~8-9 GB

**Pour suivre la progression** :
- Le build se fait en arrière-plan
- Vous pouvez vérifier avec : `docker images pulsai/monolith:latest`
- La date de création doit être récente (quelques minutes)

---

### Étape 2 : Vérifier que le Build est Terminé

Utilisez le script de vérification :

```bash
check-monolith-status.bat
```

Ou vérifiez manuellement :

```bash
docker images pulsai/monolith:latest
```

**Attendu** :
```
REPOSITORY        TAG       IMAGE ID       CREATED          SIZE
pulsai/monolith   latest    xxxxxxxxxx     X minutes ago    8.61GB
```

La colonne `CREATED` doit afficher "X minutes ago" ou "X seconds ago" (pas "8 days ago").

---

### Étape 3 : Lancer le Conteneur

Une fois le build terminé, utilisez le script de démarrage :

```bash
start-monolith-clean.bat
```

Ce script va :
1. ✅ Arrêter les anciens services
2. ✅ Vérifier que l'image existe
3. ✅ Démarrer tous les services (PulsAI, Redis, Ollama)
4. ✅ Vérifier que tout fonctionne

**Ou manuellement** :

```bash
# Arrêter les anciens conteneurs
docker-compose -f docker-compose.monolith.yaml down

# Démarrer les nouveaux
docker-compose -f docker-compose.monolith.yaml up -d

# Voir les logs
docker-compose -f docker-compose.monolith.yaml logs -f
```

---

### Étape 4 : Vérifier que Tout Fonctionne

**Vérification automatique** :
```bash
check-monolith-status.bat
```

**Vérifications manuelles** :

1. **Conteneurs en cours** :
   ```bash
   docker ps
   ```
   Vous devriez voir :
   - `pulsai-monolith` (Up)
   - `pulsai-redis` (Up, healthy)
   - `pulsai-ollama` (Up, healthy)

2. **Health checks** :
   ```bash
   # Backend
   curl http://localhost:3000/health
   
   # Ollama
   curl http://localhost:11434/api/tags
   ```

3. **Logs** :
   ```bash
   docker logs pulsai-monolith
   ```
   Vous devriez voir quelque chose comme :
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8080
   INFO:     Application startup complete.
   ```

4. **Interface Web** :
   Ouvrez votre navigateur : http://localhost:3000

---

## 🎯 Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| **Interface PulsAI** | http://localhost:3000 | Interface principale |
| **Ollama** | http://localhost:11434 | API Ollama pour les LLMs |
| **Redis** | localhost:6379 | Cache (interne) |

---

## 🔍 Dépannage

### Le conteneur s'arrête immédiatement

```bash
# Voir les logs
docker logs pulsai-monolith --tail 100

# Si vous voyez encore "ModuleNotFoundError: No module named 'open_webui'"
# Cela signifie que le build n'a pas utilisé le nouveau start.sh
# Solution : Rebuild sans cache
docker build --no-cache --build-arg USE_CUDA=false -t pulsai/monolith:latest -f Dockerfile .
```

### Port déjà utilisé

Si le port 3000 est déjà utilisé :

1. Modifiez `docker-compose.monolith.yaml` :
   ```yaml
   ports:
     - "3001:8080"  # Changer 3000 en 3001
   ```

2. Redémarrez :
   ```bash
   docker-compose -f docker-compose.monolith.yaml down
   docker-compose -f docker-compose.monolith.yaml up -d
   ```

### Vérifier l'espace disque

```bash
docker system df
```

Si besoin de nettoyer :
```bash
# Nettoyage léger
docker system prune -f

# Nettoyage complet (ATTENTION : supprime tout ce qui n'est pas utilisé)
docker system prune -a -f
```

---

## 📝 Commandes Utiles

### Démarrage/Arrêt

```bash
# Démarrer
docker-compose -f docker-compose.monolith.yaml up -d

# Arrêter
docker-compose -f docker-compose.monolith.yaml down

# Redémarrer
docker-compose -f docker-compose.monolith.yaml restart
```

### Logs

```bash
# Logs de tous les services
docker-compose -f docker-compose.monolith.yaml logs

# Logs en temps réel
docker-compose -f docker-compose.monolith.yaml logs -f

# Logs d'un service spécifique
docker logs pulsai-monolith -f
docker logs pulsai-ollama -f
docker logs pulsai-redis -f
```

### Inspection

```bash
# État des conteneurs
docker ps

# Inspecter un conteneur
docker inspect pulsai-monolith

# Entrer dans un conteneur
docker exec -it pulsai-monolith bash
```

---

## ✨ Prochaines Étapes

Une fois PulsAI démarré :

1. **Créer un compte** : http://localhost:3000
2. **Télécharger un modèle Ollama** :
   ```bash
   docker exec pulsai-ollama ollama pull llama2
   ```
3. **Commencer à discuter** avec vos LLMs !

---

## 🆘 Besoin d'Aide ?

Consultez les guides de dépannage :
- [TROUBLESHOOTING-DOCKER-FR.md](TROUBLESHOOTING-DOCKER-FR.md) - Guide complet
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Guide général
- [DOCKER_LOCAL_SETUP.md](DOCKER_LOCAL_SETUP.md) - Setup Docker

---

## 📊 Résumé des Fichiers Utiles

| Fichier | Fonction |
|---------|----------|
| `build-monolith.bat` | Construire l'image monolithe |
| `start-monolith-clean.bat` | Démarrer proprement le monolithe |
| `check-monolith-status.bat` | Vérifier l'état du monolithe |
| `diagnostic-monolith.bat` | Diagnostic complet |
| `fix-and-restart.bat` | Fix et redémarrage (GitHub) |

---

**Statut Actuel** :
- ✅ Problème identifié et corrigé
- 🔄 Build en cours (~10-15 min)
- ⏳ En attente du build pour démarrer

**Prochaine action** : Attendez que le build se termine, puis lancez `start-monolith-clean.bat`

---

_Dernière mise à jour : 11 novembre 2025_

