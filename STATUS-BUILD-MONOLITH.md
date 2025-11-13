# 📊 Status du Build PulsAI Monolith

## ✅ Build en Cours

**Date/Heure** : 11 novembre 2025, 10h10  
**Commande** : `docker build -t pulsai/monolith:latest`  
**Status** : 🔄 EN COURS

---

## 🔧 Correctif Appliqué

### Problème Identifié
```
ModuleNotFoundError: No module named 'open_webui'
```

### Solution
✅ Fichier `backend/start.sh` corrigé :
- **Avant** : `uvicorn open_webui.main:app`
- **Après** : `uvicorn pulsai.main:app`

Le module a été renommé de `open_webui` → `pulsai` mais le script de démarrage n'avait pas été mis à jour.

---

## 📈 Progression du Build

### Étapes Actuelles

```
✅ [1/50] Chargement Dockerfile
✅ [2/50] Chargement .dockerignore  
✅ [3/50] Base Python image (3.11-bookworm)
✅ [4/50] Base Node image (22-bullseye)
🔄 [5/50] Installation git dans build stage...
⏳ [6/50] npm install (Node.js dependencies)
⏳ [7/50] npm run build (Frontend build)
⏳ [8/50] pip install (Python dependencies)
⏳ [9/50] Download ML models (embeddings, whisper)
⏳ [10/50] Final assembly
```

### Temps Estimé par Étape

| Étape | Temps | Status |
|-------|-------|--------|
| Base images | 1-2 min | ✅ Fait |
| Git installation | 2-3 min | 🔄 En cours |
| npm install | 3-5 min | ⏳ À venir |
| npm build (Frontend) | 5-8 min | ⏳ À venir |
| pip install | 2-3 min | ⏳ À venir |
| ML models download | 3-5 min | ⏳ À venir |
| Final assembly | 1 min | ⏳ À venir |

**⏰ Temps Total Estimé : 15-25 minutes**

---

## 🎯 Ce qui va se Passer

### 1. Frontend Build (Node.js)
- Installation de ~2000 packages npm
- Compilation du code TypeScript/Svelte
- Bundling avec Vite
- **Taille** : ~300 MB

### 2. Backend Build (Python)
- Installation des dépendances Python
- Téléchargement des modèles ML :
  - Sentence transformers (embeddings) : ~90 MB
  - Whisper (speech-to-text) : ~150 MB
  - Tiktoken (tokenization)
- **Taille** : ~8 GB au total

### 3. Assembly Final
- Copie du frontend buildé vers l'image Python
- Configuration de l'environnement
- Setup des healthchecks

---

## 📊 Taille de l'Image Finale

```
REPOSITORY        TAG       SIZE
pulsai/monolith   latest    ~8.6 GB
```

**Composition** :
- Base OS (Debian) : ~300 MB
- Python + libraries : ~2 GB
- Node.js build artifacts : ~300 MB
- ML Models : ~500 MB
- PyTorch CPU : ~5 GB
- Application code : ~100 MB

---

## 🔍 Vérifier la Progression

### Commande 1 : Voir les images en cours de build
```bash
docker images
```

### Commande 2 : Voir les layers
```bash
docker history pulsai/monolith:latest
```

### Commande 3 : Espace disque
```bash
docker system df
```

---

## ⚠️ Points d'Attention

### Mémoire
Le build nécessite :
- **RAM** : 4-8 GB disponibles
- **Swap** : 2-4 GB recommandés
- **Disque** : 15-20 GB libres

Si vous manquez de ressources :
```bash
# Nettoyer l'espace
docker system prune -a -f

# Ou utiliser --slim pour une image plus petite
docker build --build-arg USE_SLIM=true -t pulsai/monolith:latest .
```

### Réseau
Le build télécharge ~3-4 GB de données :
- Images de base Docker
- Packages npm
- Packages Python
- Modèles ML

---

## ✅ Après le Build

### 1. Vérifier que l'image existe
```bash
docker images pulsai/monolith:latest
```

**Attendu** :
```
REPOSITORY        TAG     IMAGE ID      CREATED         SIZE
pulsai/monolith   latest  xxxxxxxxxx    X minutes ago   8.61GB
```

### 2. Lancer le conteneur
```bash
start-monolith-clean.bat
```

### 3. Vérifier les logs
```bash
docker logs pulsai-monolith -f
```

**Attendu** (sans erreur) :
```
Loading WEBUI_SECRET_KEY from file...
Generating WEBUI_SECRET_KEY
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### 4. Accéder à l'interface
http://localhost:3000

---

## 🚨 Si le Build Échoue

### Erreur : "no space left on device"
```bash
docker system prune -a -f
docker volume prune -f
```

### Erreur : "npm install failed"
```bash
# Rebuild avec plus de mémoire Node
docker build --build-arg NODE_OPTIONS="--max-old-space-size=8192" ...
```

### Erreur : "connection timeout"
```bash
# Retry le build (Docker cache les layers réussis)
docker build -t pulsai/monolith:latest -f Dockerfile .
```

### Build trop long
```bash
# Utilisez l'option slim (plus rapide, mais sans les modèles ML pré-téléchargés)
docker build --build-arg USE_SLIM=true -t pulsai/monolith:latest -f Dockerfile .
```

---

## 📞 Commandes Utiles Pendant le Build

```bash
# Voir l'utilisation disque en temps réel
docker system df

# Voir les processus Docker
docker ps -a

# Annuler le build (si nécessaire)
# Ctrl+C puis :
docker build --rm=false ...  # Le prochain build reprendra où ça s'est arrêté
```

---

## 🎬 Prochaines Actions

1. ⏳ **Attendez** que le build se termine (~15-25 min)
2. ✅ **Vérifiez** avec : `docker images pulsai/monolith:latest`
3. 🚀 **Lancez** avec : `start-monolith-clean.bat`
4. 🎉 **Profitez** de PulsAI sur http://localhost:3000

---

**🔄 Status Actuel** : Build en cours, étape installation Git  
**⏰ Temps restant estimé** : 15-20 minutes  
**💾 Espace requis** : 15-20 GB  

---

_Dernière mise à jour : 11 novembre 2025, 10:10_

