# 🔄 Guide : Rebuild Pulsai depuis GitHub

**Source** : https://github.com/Powwpol/open-webui  
**Branche** : main  
**Type** : Build automatique depuis GitHub

---

## 🎯 3 Méthodes Disponibles

### Méthode 1 : Docker Compose (Recommandé) ⚡

**Le plus simple et rapide** - Build directement depuis GitHub

```bash
# Build et start en UNE commande
docker-compose -f docker-compose.github.yaml up -d --build

# Voir les logs
docker-compose -f docker-compose.github.yaml logs -f
```

**Avantages** :
- ✅ Une seule commande
- ✅ Build automatique depuis GitHub
- ✅ Pas besoin de cloner le repo
- ✅ Images buildées et démarrées ensemble

---

### Méthode 2 : Script Automatique 🚀

**Build avec scripts pour plus de contrôle**

```bash
# Windows
.\rebuild-from-github.bat

# Linux/Mac
chmod +x build-from-github.sh
./build-from-github.sh
```

**Options** :
```bash
# Build slim (plus rapide)
.\build-from-github.sh --slim

# Build sans cache
.\build-from-github.sh --no-cache

# Build avec tag custom
.\build-from-github.sh --tag v1.0.0

# Build depuis une branche spécifique
.\build-from-github.sh --branch develop
```

---

### Méthode 3 : Manuel (Plus de contrôle) 🔧

**Pour builds personnalisés**

```bash
# 1. Clone ou pull
git clone https://github.com/Powwpol/open-webui.git pulsai
cd pulsai

# Ou si déjà cloné
git pull origin main

# 2. Build backend
docker build \
  --build-arg USE_SLIM=true \
  -t pulsai/backend:latest \
  -f Dockerfile \
  .

# 3. Build MCP
docker build \
  -t pulsai/mcp:latest \
  -f mcp-server/Dockerfile \
  mcp-server/

# 4. Start avec compose
docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## ⚡ QUICK START (Nouveau déploiement)

### Depuis zéro → Pulsai running (5 minutes)

```powershell
# 1. Créer un dossier
mkdir C:\pulsai-deploy
cd C:\pulsai-deploy

# 2. Clone le repo GitHub
git clone https://github.com/Powwpol/open-webui.git .

# 3. Build et start TOUT
docker-compose -f docker-compose.github.yaml up -d --build

# 4. Attendre 5-10 minutes (build en cours)

# 5. Vérifier
docker-compose -f docker-compose.github.yaml ps

# 6. Access
start http://localhost:8080
```

**C'EST TOUT !** 🎉

---

## 🔄 Update depuis GitHub

### Pull dernières modifications et rebuild

```bash
# Option A: Script automatique
.\update-from-github.bat

# Option B: Docker Compose
docker-compose -f docker-compose.github.yaml down
docker-compose -f docker-compose.github.yaml pull
docker-compose -f docker-compose.github.yaml up -d --build

# Option C: Manuel
git pull origin main
docker-compose -f docker-compose.pulsai.yaml build
docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## 📦 Ce qui est buildé

### Backend (pulsai/backend:github)

**Source GitHub** :
- `backend/pulsai/` - Code Python rebrandé
- `backend/requirements.txt` - Dépendances
- `backend/migrations/` - Migrations DB
- `Dockerfile` - Build instructions

**Build** :
- Base : Python 3.11
- FastAPI + Uvicorn
- RAG avec embeddings (ou slim sans embeddings)
- Taille : ~1.2GB (slim) / ~2.5GB (full)

### MCP Server (pulsai/mcp:github)

**Source GitHub** :
- `mcp-server/pulsai_mcp/` - Code MCP
- `mcp-server/pyproject.toml` - Dépendances
- `mcp-server/Dockerfile` - Build

**Build** :
- Base : Python 3.11
- Custom MCP tools
- Taille : ~500MB

---

## 🎮 Commandes Utiles

### Build

```bash
# Build depuis GitHub (docker-compose)
docker-compose -f docker-compose.github.yaml build

# Build backend seulement
docker-compose -f docker-compose.github.yaml build pulsai-backend

# Build sans cache (clean build)
docker-compose -f docker-compose.github.yaml build --no-cache

# Build avec pull (dernière version)
docker-compose -f docker-compose.github.yaml build --pull
```

### Start/Stop

```bash
# Start
docker-compose -f docker-compose.github.yaml up -d

# Stop
docker-compose -f docker-compose.github.yaml down

# Restart
docker-compose -f docker-compose.github.yaml restart

# Logs
docker-compose -f docker-compose.github.yaml logs -f

# Logs backend seulement
docker-compose -f docker-compose.github.yaml logs -f pulsai-backend
```

### Vérification

```bash
# Status services
docker-compose -f docker-compose.github.yaml ps

# Health checks
curl http://localhost:8080/health      # Backend
curl http://localhost:8001/health      # MCP
curl http://localhost:11434/api/tags   # Ollama

# Entrer dans un container
docker-compose -f docker-compose.github.yaml exec pulsai-backend bash
```

---

## 🔍 Troubleshooting

### Build échoue

**Problème** : Timeout ou erreur réseau

```bash
# Solution 1: Augmenter timeout Docker
# Docker Desktop → Settings → Docker Engine
# Ajouter: "max-concurrent-downloads": 1

# Solution 2: Clone d'abord, puis build
git clone https://github.com/Powwpol/open-webui.git pulsai
cd pulsai
docker-compose -f docker-compose.pulsai.yaml build

# Solution 3: Build avec retry
for /L %i in (1,1,3) do (
    docker-compose -f docker-compose.github.yaml build && goto :success
)
:success
```

### Erreur "context" lors du build

**Problème** : Docker ne peut pas accéder au GitHub

```bash
# Solution: Clone localement puis build
git clone https://github.com/Powwpol/open-webui.git
cd open-webui
docker build -t pulsai/backend:latest -f Dockerfile .
```

### Port déjà utilisé

```bash
# Changer dans docker-compose.github.yaml
services:
  pulsai-backend:
    ports:
      - "8081:8080"  # Utiliser 8081 au lieu de 8080
```

### Manque d'espace disque

```bash
# Nettoyer
docker system prune -a
docker volume prune

# Vérifier espace
docker system df
```

---

## 📊 Comparaison Build Sources

| Source | Avantages | Inconvénients | Commande |
|--------|-----------|---------------|----------|
| **GitHub Direct** | Toujours à jour, pas de clone | Plus lent, besoin internet | `docker-compose -f docker-compose.github.yaml up` |
| **Local Files** | Plus rapide, offline | Doit sync manuellement | `./build-local.sh` |
| **Clone GitHub** | Contrôle version, offline après clone | Doit pull pour update | `git pull && docker build` |

---

## 🚀 Workflow Équipe (4 personnes)

### Personne 1 : Setup initial

```bash
# Clone
git clone https://github.com/Powwpol/open-webui.git pulsai
cd pulsai

# Build et start
docker-compose -f docker-compose.github.yaml up -d --build

# Partager l'URL avec l'équipe
# http://VOTRE-IP:8080
```

### Personnes 2-4 : Rejoindre

**Option A** : Utiliser l'instance de Personne 1
```
Accéder à : http://IP-PERSONNE-1:8080
```

**Option B** : Déployer leur propre instance
```bash
git clone https://github.com/Powwpol/open-webui.git
cd open-webui
docker-compose -f docker-compose.github.yaml up -d --build
```

### Mise à jour pour tous

```bash
# Chaque personne exécute
.\update-from-github.bat

# Ou
git pull origin main
docker-compose -f docker-compose.github.yaml up -d --build
```

---

## 📈 Automatisation (CI/CD)

### GitHub Actions (optionnel)

Créer `.github/workflows/rebuild.yml` :

```yaml
name: Rebuild Pulsai

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Backend
        run: docker build -t pulsai/backend:latest -f Dockerfile .
      
      - name: Build MCP
        run: docker build -t pulsai/mcp:latest -f mcp-server/Dockerfile mcp-server/
      
      - name: Push to Registry (optionnel)
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push pulsai/backend:latest
          docker push pulsai/mcp:latest
```

---

## 🎯 Résumé Commandes

### Build Rapide

```bash
# Build et start depuis GitHub
docker-compose -f docker-compose.github.yaml up -d --build
```

### Update

```bash
# Pull + rebuild + restart
.\update-from-github.bat
```

### Rebuild Complet

```bash
# Stop + clean build + start
.\rebuild-from-github.bat
```

---

## ✅ Checklist Rebuild

Avant de rebuild depuis GitHub :

- [ ] Git installé
- [ ] Docker running
- [ ] Connexion internet active
- [ ] 20GB espace disque disponible
- [ ] Port 8080 libre
- [ ] Fichiers .env configurés (optionnel)

Après rebuild :

- [ ] Images créées (docker images | findstr pulsai)
- [ ] Services running (docker ps)
- [ ] Backend accessible (http://localhost:8080/health)
- [ ] MCP accessible (http://localhost:8001/health)
- [ ] Interface web (http://localhost:8080)

---

## 💡 Best Practices

### Pour Développement

```bash
# Build slim (plus rapide)
docker-compose -f docker-compose.github.yaml build --build-arg USE_SLIM=true

# Logs en temps réel
docker-compose -f docker-compose.github.yaml logs -f --tail=100
```

### Pour Production

```bash
# Build avec tag de version
docker build --tag pulsai/backend:v1.0.0 -f Dockerfile .

# Pousser vers registry
docker tag pulsai/backend:v1.0.0 registry.example.com/pulsai/backend:v1.0.0
docker push registry.example.com/pulsai/backend:v1.0.0
```

---

## 🆘 Support

**Scripts disponibles** :
- `rebuild-from-github.bat` - Rebuild complet
- `update-from-github.bat` - Update et rebuild
- `build-from-github.bat` - Build depuis GitHub
- `COMPLETE-UPLOAD.bat` - Upload vers votre GitHub

**Documentation** :
- `PUSH-GITHUB-INSTRUCTIONS.md` - Guide push GitHub
- `DOCKER_PULSAI.md` - Guide Docker complet
- `GITHUB-SETUP.md` - Setup GitHub repo

---

**Rebuild depuis GitHub en 1 commande** :  
`docker-compose -f docker-compose.github.yaml up -d --build` 🚀

