# 🚀 Instructions : Pousser Pulsai vers GitHub

**Status** : ✅ Repo Git préparé localement  
**Commit** : ✅ Créé (613 fichiers, 56K+ lignes)  
**Prêt à pousser** : ✅ OUI

---

## 📝 Ce qui a été fait

✅ **Git configuré** :
- User: Paulo
- Email: paulo@pulsai.local
- Branch: pulsai

✅ **Commit créé** :
- 613 fichiers ajoutés/modifiés
- 56,203 insertions
- Rebranding complet Open WebUI → Pulsai

✅ **Structure renommée** :
- `backend/open_webui/` → `backend/pulsai/`
- package.json → `"name": "pulsai"`
- pyproject.toml → `name = "pulsai"`

---

## 🎯 ÉTAPES SUIVANTES (Simple et Rapide)

### Étape 1 : Créer le Repo sur GitHub (2 min)

1. **Ouvrir** : https://github.com/new

2. **Remplir le formulaire** :
   ```
   Repository name:    pulsai
   
   Description:        Pulsai - AI Assistant Platform avec support MCP 
                       (basé sur Open WebUI, usage <50 users)
   
   Visibility:         🔒 Private (RECOMMANDÉ)
   
   ❌ Ne PAS cocher :
      - Add a README file
      - Add .gitignore
      - Choose a license
   ```

3. **Cliquer** : "Create repository"

4. **GitHub va afficher** une page avec des instructions

### Étape 2 : Pousser depuis votre PC (1 min)

**Ouvrir PowerShell** dans `C:\Users\paulo\.pulsai\pulsai` et exécuter :

```powershell
# Remplacer VOTRE-USERNAME par votre username GitHub
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git

# Renommer la branche en main
git branch -M main

# Pousser vers GitHub
git push -u origin main
```

### Étape 3 : Authentification GitHub

**Si demande de mot de passe** :

⚠️ **GitHub n'accepte PLUS les mots de passe depuis 2021**

**Solution** : Utiliser un Personal Access Token

1. Aller sur : https://github.com/settings/tokens
2. "Generate new token" → "Tokens (classic)"
3. Nom du token : `pulsai-push`
4. Expiration : 90 jours (ou No expiration)
5. **Cocher** : `repo` (Full control of private repositories)
6. "Generate token"
7. **COPIER le token** (ne sera plus visible après!)
8. Utiliser comme mot de passe lors du push

**Exemple** :
```
Username: votre-username
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (le token)
```

---

## ⚡ Méthode Ultra-Rapide (Script Automatique)

**J'ai créé un script pour vous !**

### Windows

```powershell
# Remplacer VOTRE-USERNAME par votre username GitHub
.\init-github.bat VOTRE-USERNAME
```

Puis après avoir créé le repo sur GitHub :

```powershell
.\push-to-github.bat
```

### Linux/Mac

```bash
# Remplacer VOTRE-USERNAME par votre username GitHub
./init-github.sh VOTRE-USERNAME
```

---

## 🔍 Vérification

Une fois pushé, vérifier sur GitHub :

```
https://github.com/VOTRE-USERNAME/pulsai
```

Vous devriez voir :
- ✅ 613 fichiers
- ✅ Commit "🎉 Rebranding complet: Open WebUI → Pulsai"
- ✅ README-PULSAI.md affiché
- ✅ Toute la structure (backend/, src/, docker/, etc.)

---

## 📊 Informations sur le Commit

```
Commit: 4b2d5e656 (exemple)
Author: Paulo <paulo@pulsai.local>
Date: 26 octobre 2025

Fichiers changés: 613
Insertions: 56,203
Suppressions: 1,597

Structure:
- backend/pulsai/ (nouveau)
- backend/pulsai_old/ (backup)
- backend/open_webui/ (supprimé)
- src/ (frontend modifié)
- docker/ (configurations)
- mcp-server/ (custom MCP)
- 58 langues mises à jour
```

---

## 🎨 Personnaliser votre Repo GitHub

### Après le premier push

1. **Ajouter Topics** :
   - Sur votre repo → About → ⚙️ (roue dentée)
   - Topics : `ai`, `chatbot`, `mcp`, `docker`, `fastapi`, `svelte`, `ollama`

2. **Ajouter Description** :
   ```
   Pulsai - Plateforme d'Assistant IA avec support MCP multi-protocole
   (HTTPS, npx, Docker, WebSocket, SSE)
   ```

3. **Créer une Release** (optionnel) :
   - Releases → "Create a new release"
   - Tag : `v1.0.0`
   - Title : `Pulsai v1.0.0 - Initial Release`
   - Description : Voir exemple ci-dessous

### Exemple Release Notes

```markdown
## 🎉 Pulsai v1.0.0 - First Release

### Fonctionnalités

- ✅ Rebranding complet Open WebUI → Pulsai
- ✅ Configuration MCP avec 5 protocoles (HTTP/HTTPS, npx, Docker, WebSocket, SSE)
- ✅ Support multi-backend (OpenAI, Ollama, Anthropic, Google)
- ✅ Interface en français
- ✅ 58 langues supportées
- ✅ RAG avancé avec vector databases
- ✅ Docker ready avec compose files
- ✅ MCP custom server inclus

### Basé sur
Open WebUI v0.6.32

### Licence
Usage autorisé : 4 utilisateurs (<50)  
Conforme clause 5.i Open WebUI License

### Installation

Voir [README-PULSAI.md](./README-PULSAI.md)
```

---

## 🐛 Troubleshooting

### Erreur : "remote origin already exists"

```powershell
git remote remove origin
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git
```

### Erreur : "Authentication failed"

- Vérifiez que vous utilisez un **Personal Access Token**, pas un mot de passe
- Le token doit avoir le scope `repo`
- Utilisez le token comme mot de passe

### Erreur : "Repository not found"

- Vérifiez que le repo est bien créé sur GitHub
- Vérifiez l'URL : `https://github.com/VOTRE-USERNAME/pulsai.git`
- Vérifiez votre username GitHub

### Erreur : "failed to push some refs"

Le repo GitHub existe déjà avec du contenu :

```powershell
# Option 1: Force push (⚠️ écrase tout sur GitHub)
git push -u origin main --force

# Option 2: Pull d'abord puis push
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Fichier trop gros (>100MB)

```powershell
# Voir les gros fichiers
git ls-files -z | xargs -0 du -h | sort -rh | head -20

# Les ajouter au .gitignore
echo "fichier-trop-gros.bin" >> .gitignore
git rm --cached fichier-trop-gros.bin
git commit -m "Remove large file"
```

---

## 📚 Commandes Git Utiles

```powershell
# Voir l'historique
git log --oneline

# Voir les remotes
git remote -v

# Voir les fichiers modifiés
git status

# Annuler des changements (avant commit)
git restore fichier

# Créer une nouvelle branche
git checkout -b feature/nouvelle-fonction

# Pousser une nouvelle branche
git push -u origin feature/nouvelle-fonction
```

---

## 🎊 Après le Push Réussi

### Votre repo sera disponible à :
```
https://github.com/VOTRE-USERNAME/pulsai
```

### Vous pourrez :
- ✅ Cloner sur d'autres machines
- ✅ Collaborer avec votre équipe (4 users)
- ✅ Créer des branches pour features
- ✅ Utiliser Issues pour tracker bugs
- ✅ Créer des Pull Requests
- ✅ Utiliser GitHub Actions (CI/CD)

---

## 🔐 Sécurité

### ⚠️ IMPORTANT : Vérifier qu'aucun secret n'est dans le repo

```powershell
# Rechercher des patterns de secrets
git log -p | Select-String -Pattern "API_KEY|SECRET|PASSWORD|TOKEN"

# Vérifier les fichiers .env
Get-ChildItem -Recurse -Filter ".env*" | Select-Object FullName
```

**Si vous trouvez des secrets** :
1. Les supprimer du repo
2. Les ajouter à `.gitignore`
3. Regénérer les secrets compromis
4. Utiliser `git-filter-repo` pour nettoyer l'historique (avancé)

---

## ✅ Checklist Avant Push

- [ ] Repo créé sur GitHub
- [ ] Git remote configuré
- [ ] Aucun fichier .env dans le repo
- [ ] Aucune API key dans le code
- [ ] .gitignore correctement configuré
- [ ] Commit message descriptif
- [ ] Personal Access Token prêt

---

## 🎬 Commandes Complètes (Copier-Coller)

**Remplacer `VOTRE-USERNAME` et `VOTRE-TOKEN` par vos valeurs** :

```powershell
# 1. Ajouter le remote
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git

# 2. Renommer la branche
git branch -M main

# 3. Pousser (va demander username + token)
git push -u origin main

# Si vous voulez éviter de taper le token à chaque fois:
git remote set-url origin https://VOTRE-USERNAME:VOTRE-TOKEN@github.com/VOTRE-USERNAME/pulsai.git
```

---

**Prêt à pousser ! Suivez les étapes ci-dessus.** 🚀

Si vous rencontrez un problème, consultez la section Troubleshooting.

