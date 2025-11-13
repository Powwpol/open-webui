# 🔧 Guide de Dépannage Docker - PulsAI

## 🚨 Problèmes Courants et Solutions

### 1. Le conteneur s'arrête immédiatement au démarrage

#### Symptôme
```bash
docker ps -a
# Montre: Exited (1) xxx ago
```

#### Causes possibles

**A. Erreur `ModuleNotFoundError: No module named 'open_webui'`**

✅ **SOLUTION** : Le script `start.sh` a été corrigé pour utiliser `pulsai.main:app` au lieu de `open_webui.main:app`.

Pour appliquer le correctif :
```bash
# Reconstruire l'image
docker-compose -f docker-compose.github.yaml build --no-cache pulsai-backend

# Redémarrer
docker-compose -f docker-compose.github.yaml up -d
```

Ou utilisez le script automatique :
```bash
fix-and-restart.bat
```

**B. Problème de dépendances Python**

Vérifier les logs :
```bash
docker logs pulsai-backend-github --tail 100
```

Si vous voyez des erreurs d'import, reconstruisez sans cache :
```bash
docker-compose -f docker-compose.github.yaml build --no-cache
```

**C. Base de données corrompue**

```bash
# Supprimer le volume de données
docker volume rm pulsai-data-github

# Redémarrer (créera une nouvelle DB)
docker-compose -f docker-compose.github.yaml up -d
```

⚠️ **ATTENTION** : Cela supprimera toutes vos données (conversations, modèles, etc.)

---

### 2. Docker Desktop ne démarre pas

#### Symptôme
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

#### Solutions

**Option 1 : Démarrage manuel**
1. Recherchez "Docker Desktop" dans le menu Démarrer
2. Lancez l'application
3. Attendez que l'icône Docker devienne verte dans la barre des tâches
4. Réessayez votre commande

**Option 2 : Démarrage automatique**
Le script `diagnostic-monolith.bat` tente de démarrer Docker automatiquement.

**Option 3 : Vérifier les services Windows**
```powershell
# En tant qu'administrateur
Get-Service | Where-Object {$_.Name -like "*docker*"}

# Démarrer le service si nécessaire
Start-Service com.docker.service
```

---

### 3. Port déjà utilisé

#### Symptôme
```
Error: Bind for 0.0.0.0:8080 failed: port is already allocated
```

#### Solutions

**Option 1 : Trouver et arrêter le processus**
```powershell
# Trouver le processus
netstat -ano | findstr :8080

# Arrêter le processus (remplacer PID)
taskkill /PID <PID> /F
```

**Option 2 : Changer le port dans docker-compose.github.yaml**
```yaml
pulsai-backend:
  ports:
    - "8081:8080"  # Utiliser 8081 au lieu de 8080
```

Ensuite :
```bash
docker-compose -f docker-compose.github.yaml down
docker-compose -f docker-compose.github.yaml up -d
```

---

### 4. Problème de connexion à Redis ou Ollama

#### Symptôme
```
Connection refused: redis://pulsai-redis:6379
```

#### Diagnostic
```bash
# Vérifier que tous les services sont démarrés
docker-compose -f docker-compose.github.yaml ps

# Vérifier les health checks
docker ps --format "table {{.Names}}\t{{.Status}}"
```

#### Solutions

**Si Redis n'est pas démarré :**
```bash
docker-compose -f docker-compose.github.yaml up -d pulsai-redis
docker logs pulsai-redis
```

**Si Ollama n'est pas démarré :**
```bash
docker-compose -f docker-compose.github.yaml up -d pulsai-ollama
docker logs pulsai-ollama
```

**Redémarrer tous les services dans le bon ordre :**
```bash
docker-compose -f docker-compose.github.yaml down
docker-compose -f docker-compose.github.yaml up -d pulsai-redis
timeout /t 5
docker-compose -f docker-compose.github.yaml up -d pulsai-ollama
timeout /t 10
docker-compose -f docker-compose.github.yaml up -d pulsai-backend
```

---

### 5. Espace disque insuffisant

#### Symptôme
```
no space left on device
```

#### Diagnostic
```bash
# Vérifier l'utilisation de l'espace Docker
docker system df

# Afficher en détail
docker system df -v
```

#### Solutions

**Nettoyage léger (garde les images utilisées) :**
```bash
docker system prune -f
```

**Nettoyage complet (supprime tout ce qui n'est pas utilisé) :**
```bash
docker system prune -a --volumes -f
```

⚠️ **ATTENTION** : Cela supprimera toutes les images non utilisées et tous les volumes non attachés.

**Nettoyage ciblé :**
```bash
# Supprimer les conteneurs arrêtés
docker container prune -f

# Supprimer les images non utilisées
docker image prune -a -f

# Supprimer les volumes non utilisés
docker volume prune -f

# Supprimer les réseaux non utilisés
docker network prune -f
```

---

### 6. Image de build corrompue

#### Symptôme
Le conteneur ne démarre pas même après reconstruction.

#### Solution
```bash
# 1. Arrêter tous les conteneurs
docker-compose -f docker-compose.github.yaml down

# 2. Supprimer l'image
docker rmi pulsai/backend:github -f
docker rmi pulsai/mcp:github -f

# 3. Nettoyer le cache de build
docker builder prune -a -f

# 4. Reconstruire
docker-compose -f docker-compose.github.yaml build --no-cache

# 5. Redémarrer
docker-compose -f docker-compose.github.yaml up -d
```

---

### 7. Logs ne s'affichent pas ou sont vides

#### Solutions

```bash
# Vérifier que le conteneur existe
docker ps -a | findstr pulsai

# Voir TOUS les logs depuis le début
docker logs pulsai-backend-github

# Voir les logs en temps réel
docker logs pulsai-backend-github -f

# Voir les 200 dernières lignes
docker logs pulsai-backend-github --tail 200

# Voir les logs avec timestamp
docker logs pulsai-backend-github -t
```

---

### 8. Healthcheck échoue

#### Symptôme
```
Health: unhealthy
```

#### Diagnostic
```bash
# Vérifier le health check
docker inspect pulsai-backend-github | findstr Health -A 20

# Tester manuellement le endpoint
curl http://localhost:8080/health
```

#### Solution

**Si le service n'est pas encore prêt :**
Attendez 60 secondes (le `start_period` dans le healthcheck).

**Si le service est prêt mais le healthcheck échoue :**
```bash
# Vérifier les logs
docker logs pulsai-backend-github --tail 100

# Redémarrer le conteneur
docker restart pulsai-backend-github
```

---

### 9. Problème de réseau entre conteneurs

#### Symptôme
```
Could not connect to pulsai-ollama
```

#### Diagnostic
```bash
# Vérifier le réseau
docker network ls

# Inspecter le réseau
docker network inspect pulsai-network-github

# Vérifier que les conteneurs sont sur le même réseau
docker inspect pulsai-backend-github | findstr NetworkMode
docker inspect pulsai-ollama | findstr NetworkMode
```

#### Solution
```bash
# Recréer le réseau
docker-compose -f docker-compose.github.yaml down
docker network rm pulsai-network-github
docker-compose -f docker-compose.github.yaml up -d
```

---

### 10. Permission denied sur les volumes

#### Symptôme
```
Permission denied: '/app/backend/data'
```

#### Solution Windows
Assurez-vous que Docker Desktop a accès au disque :
1. Docker Desktop → Settings → Resources → File Sharing
2. Ajoutez le chemin de votre projet
3. Redémarrez Docker Desktop

---

## 🛠️ Commandes de Diagnostic Utiles

### Informations système
```bash
# Version Docker
docker --version
docker-compose --version

# Info Docker
docker info

# Espace disque
docker system df -v
```

### État des conteneurs
```bash
# Tous les conteneurs
docker ps -a

# Conteneurs PulsAI seulement
docker ps -a | findstr pulsai

# Avec format personnalisé
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"
```

### Logs et débogage
```bash
# Logs d'un service spécifique
docker-compose -f docker-compose.github.yaml logs pulsai-backend

# Logs de tous les services
docker-compose -f docker-compose.github.yaml logs

# Logs en temps réel
docker-compose -f docker-compose.github.yaml logs -f

# Dernières 100 lignes
docker-compose -f docker-compose.github.yaml logs --tail 100
```

### Inspection
```bash
# Inspecter un conteneur
docker inspect pulsai-backend-github

# Voir les variables d'environnement
docker inspect pulsai-backend-github | findstr -A 50 "Env"

# Voir les mounts/volumes
docker inspect pulsai-backend-github | findstr -A 20 "Mounts"
```

### Interaction avec les conteneurs
```bash
# Entrer dans un conteneur
docker exec -it pulsai-backend-github bash

# Exécuter une commande
docker exec pulsai-backend-github ls -la /app/backend

# Vérifier Python dans le conteneur
docker exec pulsai-backend-github python -c "import pulsai; print('OK')"
```

---

## 📋 Checklist de Dépannage

Lorsque vous rencontrez un problème, suivez cette checklist :

- [ ] Docker Desktop est-il démarré ? (icône verte dans la barre des tâches)
- [ ] Les conteneurs sont-ils en cours d'exécution ? (`docker ps`)
- [ ] Y a-t-il des erreurs dans les logs ? (`docker logs <container>`)
- [ ] Les ports sont-ils disponibles ? (`netstat -ano | findstr :8080`)
- [ ] Y a-t-il assez d'espace disque ? (`docker system df`)
- [ ] Les healthchecks passent-ils ? (`docker ps` - colonne STATUS)
- [ ] Le réseau fonctionne-t-il ? (`docker network ls`)
- [ ] Les volumes sont-ils montés ? (`docker inspect <container>`)

---

## 🚀 Scripts de Dépannage Automatiques

### 1. Diagnostic complet
```bash
diagnostic-monolith.bat
```

### 2. Fix et redémarrage
```bash
fix-and-restart.bat
```

### 3. Nettoyage complet et redémarrage
```bash
docker-compose -f docker-compose.github.yaml down -v
docker system prune -a -f
docker-compose -f docker-compose.github.yaml build --no-cache
docker-compose -f docker-compose.github.yaml up -d
```

---

## 📞 Support

Si le problème persiste :

1. **Collectez les informations** :
   ```bash
   # Version Docker
   docker --version
   
   # État des conteneurs
   docker ps -a
   
   # Logs complets
   docker-compose -f docker-compose.github.yaml logs > logs.txt
   
   # Info système
   docker system df
   docker info
   ```

2. **Créez un rapport d'erreur** avec :
   - Description du problème
   - Étapes pour reproduire
   - Messages d'erreur complets
   - Fichier logs.txt

3. **Vérifiez la documentation** :
   - [README.md](README.md)
   - [DOCKER_LOCAL_SETUP.md](DOCKER_LOCAL_SETUP.md)
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🔄 Remise à zéro complète

Si rien ne fonctionne, voici comment tout réinitialiser :

```bash
# ATTENTION : Cela supprimera TOUTES vos données PulsAI

# 1. Arrêter tous les conteneurs PulsAI
docker-compose -f docker-compose.github.yaml down -v
docker-compose -f docker-compose.monolith.yaml down -v
docker-compose -f docker-compose.local.yaml down -v

# 2. Supprimer les images PulsAI
docker rmi pulsai/backend:github -f
docker rmi pulsai/mcp:github -f
docker rmi pulsai/monolith:latest -f

# 3. Supprimer les volumes PulsAI
docker volume rm pulsai-data-github
docker volume rm pulsai-redis-data
docker volume rm pulsai-ollama-data

# 4. Nettoyer le système Docker
docker system prune -a --volumes -f

# 5. Reconstruire et redémarrer
docker-compose -f docker-compose.github.yaml build --no-cache
docker-compose -f docker-compose.github.yaml up -d

# 6. Vérifier
docker ps
docker-compose -f docker-compose.github.yaml logs -f
```

---

**Dernière mise à jour** : Novembre 2025  
**Version** : 1.0.0

