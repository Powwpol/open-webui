# 🚀 Guide : Créer un Repo GitHub pour Pulsai

**Projet** : Pulsai  
**Type** : Nouveau dépôt GitHub  
**Visibilité** : Privé (recommandé pour usage interne)

---

## 📋 Prérequis

- [x] Compte GitHub
- [x] Git installé localement
- [x] Projet Pulsai rebrandé (✅ fait)
- [x] Terminal/PowerShell

---

## 🚀 Étape 1 : Créer le Repo sur GitHub

### Option A : Via Interface Web (Recommandé)

1. **Aller sur GitHub** : https://github.com/new

2. **Configuration du repo** :
   ```
   Repository name:    pulsai
   Description:        Pulsai - AI Assistant Platform (Fork Open WebUI)
   Visibility:         🔒 Private (recommandé)
   
   ❌ Ne PAS initialiser avec :
      - README
      - .gitignore  
      - License
   ```

3. **Créer le repository** : Cliquer sur "Create repository"

4. **Copier l'URL** fournie :
   ```
   https://github.com/VOTRE-USERNAME/pulsai.git
   ```

### Option B : Via GitHub CLI (Alternative)

```bash
# Installer GitHub CLI si pas déjà fait
# https://cli.github.com/

# Créer le repo
gh repo create pulsai --private --description "Pulsai - AI Assistant Platform"
```

---

## 🔧 Étape 2 : Initialiser Git Localement

### Ouvrir PowerShell dans le dossier Pulsai

```powershell
cd C:\Users\paulo\.pulsai\pulsai
```

### Vérifier l'état Git actuel

```powershell
# Vérifier si déjà un repo Git
git status

# Si erreur "not a git repository", initialiser :
git init
```

### Si git remote existe déjà (pointe vers Open WebUI)

```powershell
# Voir les remotes actuels
git remote -v

# Si remote "origin" pointe vers open-webui, le supprimer
git remote remove origin
```

---

## 📤 Étape 3 : Préparer le Commit Initial

### Vérifier les fichiers à inclure

```powershell
# Voir tous les fichiers
git status

# Vérifier que .gitignore est OK
cat .gitignore
```

### Ajouter tous les fichiers

```powershell
# Ajouter tous les fichiers
git add .

# Ou sélectif si vous préférez
git add backend/
git add src/
git add static/
git add docker/
git add config/
git add mcp-server/
git add *.md
git add *.json
git add *.yaml
git add *.bat
git add *.sh
```

### Créer le commit initial

```powershell
git commit -m "🎉 Initial commit: Pulsai rebrandé (fork Open WebUI)

- Rebranding complet Open WebUI → Pulsai
- 102 fichiers modifiés, ~822 occurrences remplacées
- Configuration MCP complète (HTTPS, npx, Docker, WebSocket, SSE)
- Support 4 utilisateurs en local
- Charte graphique Pulsai appliquée
- Interface en français

Basé sur Open WebUI v0.6.32
Conforme licence Open WebUI (clause 5.i: <50 utilisateurs)"
```

---

## 🌐 Étape 4 : Pousser vers GitHub

### Ajouter le remote GitHub

```powershell
# Remplacer VOTRE-USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git

# Vérifier
git remote -v
```

### Pousser le code

```powershell
# Créer et pousser sur la branche main
git branch -M main
git push -u origin main
```

### Si demande d'authentification

**GitHub a désactivé les mots de passe en 2021.**  
Utilisez un **Personal Access Token** :

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Cocher : `repo` (full control)
4. Copier le token
5. Utiliser comme mot de passe lors du push

**Ou configurez SSH** :
```powershell
# Générer clé SSH
ssh-keygen -t ed25519 -C "votre-email@example.com"

# Ajouter à GitHub
cat ~/.ssh/id_ed25519.pub

# Utiliser SSH remote au lieu de HTTPS
git remote set-url origin git@github.com:VOTRE-USERNAME/pulsai.git
```

---

## 📊 Étape 5 : Vérifier sur GitHub

1. Aller sur : `https://github.com/VOTRE-USERNAME/pulsai`
2. Vérifier :
   - [x] Tous les fichiers sont là
   - [x] README.md s'affiche
   - [x] Commit initial visible
   - [x] Branches (main)

---

## 🎨 Étape 6 : Personnaliser le Repo GitHub

### Ajouter une description

Sur la page GitHub du repo :
1. Cliquer "⚙️ Settings"
2. Description : `Pulsai - AI Assistant Platform avec support MCP multi-protocole`
3. Topics : `ai`, `chatbot`, `mcp`, `docker`, `fastapi`, `svelte`

### Créer un README.md Pulsai (recommandé)

Votre README.md actuel peut encore avoir des références Open WebUI.  
Je peux vous créer un nouveau README.md spécifique Pulsai si besoin.

### Ajouter .gitignore spécifique

Votre `.gitignore` est déjà bon, mais vérifiez qu'il ignore :
```
node_modules/
__pycache__/
*.pyc
.env
.env.*
build/
dist/
.svelte-kit/
backend/data/
*.db
```

---

## 🔒 Étape 7 : Sécurité

### Fichiers sensibles à NE PAS pusher

Vérifiez que ces fichiers sont dans `.gitignore` :
```
.env
.env.*
*.key
*.pem
*.crt
config.local.*
backend/data/
webui.db
*.secret
```

### Vérifier qu'aucun secret n'a été pushé

```powershell
# Rechercher des patterns de secrets
git log -p | Select-String -Pattern "API_KEY|SECRET|PASSWORD"
```

---

## 🔄 Workflow Git pour l'Avenir

### Branches recommandées

```bash
main              # Production stable
develop           # Développement
feature/xxx       # Nouvelles fonctionnalités
hotfix/xxx        # Corrections urgentes
```

### Workflow de base

```powershell
# Créer une branche pour une feature
git checkout -b feature/nouvelle-fonction

# Faire vos modifications...

# Commit
git add .
git commit -m "feat: ajout nouvelle fonction"

# Pousser la branche
git push -u origin feature/nouvelle-fonction

# Merger dans main (via Pull Request sur GitHub ou localement)
git checkout main
git merge feature/nouvelle-fonction
git push origin main
```

---

## 📦 Étape 8 : GitHub Actions (Optionnel)

### CI/CD pour builds automatiques

Créer `.github/workflows/docker-build.yml` :

```yaml
name: Build Docker Images

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Backend
        run: |
          docker build -t pulsai/backend:latest -f docker/pulsai-backend.Dockerfile .
      
      - name: Build Frontend
        run: |
          docker build -t pulsai/frontend:latest -f docker/pulsai-frontend.Dockerfile .
```

---

## 🏷️ Versioning & Releases

### Créer votre première release

```powershell
# Tagger la version initiale
git tag -a v1.0.0 -m "Pulsai v1.0.0 - Initial release rebrandé"

# Pousser le tag
git push origin v1.0.0
```

Sur GitHub :
1. Releases → Create a new release
2. Tag : `v1.0.0`
3. Title : `Pulsai v1.0.0 - Initial Release`
4. Description :
   ```markdown
   ## 🎉 Première Release Pulsai
   
   - ✅ Rebranding complet Open WebUI → Pulsai
   - ✅ Configuration MCP multi-protocole (HTTPS, npx, Docker, WebSocket, SSE)
   - ✅ Support 4 utilisateurs en local
   - ✅ Interface en français
   
   Basé sur Open WebUI v0.6.32
   ```

---

## 📚 Commandes Rapides (Référence)

```powershell
# État du repo
git status

# Historique
git log --oneline

# Branches
git branch -a

# Pull dernières modifs (si travail en équipe)
git pull origin main

# Pousser vos modifs
git add .
git commit -m "Votre message"
git push origin main

# Voir les remotes
git remote -v

# Cloner ailleurs
git clone https://github.com/VOTRE-USERNAME/pulsai.git
```

---

## ⚠️ Important : Licence Open WebUI

### Attribution Requise

Même si rebrandé, vous devez :
1. ✅ Garder les fichiers LICENSE, CODE_OF_CONDUCT (déjà fait)
2. ✅ Mentionner dans README que c'est basé sur Open WebUI
3. ✅ Respecter la limite <50 utilisateurs

### Suggestion README.md

Ajouter en haut :
```markdown
# Pulsai

> Basé sur [Open WebUI](https://github.com/open-webui/open-webui) v0.6.32  
> Usage interne - <50 utilisateurs (conforme licence clause 5.i)
```

---

## 🎯 Checklist Finale

Avant de pousser vers GitHub :

- [ ] Vérifier que `.env` est dans `.gitignore`
- [ ] Aucun secret/API key dans le code
- [ ] README.md mentionne attribution Open WebUI
- [ ] LICENSE original conservé
- [ ] Fichiers de build exclus (.gitignore)
- [ ] Tests passent (si applicable)

---

## 🆘 Troubleshooting

### Erreur : "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git
```

### Erreur : "Authentication failed"
- Utiliser Personal Access Token au lieu du mot de passe
- Ou configurer SSH

### Fichiers trop gros (>100MB)
```powershell
# Voir les gros fichiers
git ls-files -z | xargs -0 du -h | sort -rh | head -20

# Ajouter à .gitignore et supprimer du cache
git rm --cached path/to/large/file
```

### Conflit avec .gitignore
```powershell
# Forcer l'ajout si nécessaire
git add -f fichier

# Ou nettoyer le cache
git rm -r --cached .
git add .
```

---

## 📞 Support

### Documentation Git/GitHub
- [Git Basics](https://git-scm.com/book/en/v2)
- [GitHub Docs](https://docs.github.com/)
- [GitHub CLI](https://cli.github.com/)

### Commandes utiles
```powershell
# Aide Git
git --help
git commit --help

# Annuler dernier commit (garder les fichiers)
git reset --soft HEAD~1

# Voir différences avant commit
git diff

# Historique d'un fichier
git log --follow -- path/to/file
```

---

**Prêt à pousser vers GitHub !** 🚀  
Suivez les étapes ci-dessus pour créer votre repo Pulsai.

