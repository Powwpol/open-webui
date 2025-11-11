# 🚀 Upload Complet Pulsai vers GitHub - GUIDE SIMPLE

**Tout est prêt !** Le commit est créé avec vos 613 fichiers. Il reste 3 étapes simples.

---

## ⚡ MÉTHODE RAPIDE (5 minutes)

### Étape 1 : Créer le Repo GitHub (2 min) 🌐

1. **Ouvrir** : https://github.com/new

2. **Remplir** :
   - **Repository name** : `pulsai`
   - **Description** : `Pulsai - AI Assistant avec MCP (4 users, usage interne)`
   - **Visibilité** : 🔒 **Private** (RECOMMANDÉ)
   - ❌ **NE RIEN COCHER** en dessous (pas de README, pas de .gitignore, pas de license)

3. **Cliquer** : **"Create repository"**

4. **GitHub affiche une page** → Ignorez les instructions, suivez les miennes ci-dessous

---

### Étape 2 : Configuration (30 secondes) 🔧

**Ouvrir PowerShell** dans votre dossier Pulsai :

```powershell
cd C:\Users\paulo\.pulsai\pulsai
```

**Remplacer `VOTRE-USERNAME` par votre username GitHub** et exécuter :

```powershell
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git
git branch -M main
```

**Exemple** :
```powershell
# Si votre username GitHub est "paulodev"
git remote add origin https://github.com/paulodev/pulsai.git
git branch -M main
```

---

### Étape 3 : Push TOUT vers GitHub (2 min) 📤

```powershell
git push -u origin main
```

**GitHub va vous demander** :
- **Username** : Votre username GitHub
- **Password** : ⚠️ **PAS votre mot de passe !** → Utilisez un **Token**

---

## 🔑 Créer un Personal Access Token (1ère fois seulement)

**GitHub n'accepte plus les mots de passe depuis 2021.**

### Étapes :

1. **Aller sur** : https://github.com/settings/tokens

2. **Cliquer** : "Generate new token" → **"Tokens (classic)"**

3. **Configuration** :
   - **Note** : `pulsai-upload`
   - **Expiration** : 90 days (ou "No expiration" si vous voulez)
   - **Select scopes** : ✅ Cocher **`repo`** (et rien d'autre)

4. **Cliquer** : "Generate token"

5. **COPIER LE TOKEN** immédiatement (impossible de le revoir après !)
   - Format : `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

6. **Utiliser ce token comme mot de passe** lors du push

---

## 📋 COMMANDES COMPLÈTES (Copier-Coller)

**Remplacez `VOTRE-USERNAME` par votre username GitHub** :

```powershell
# 1. Dans PowerShell, aller dans le dossier
cd C:\Users\paulo\.pulsai\pulsai

# 2. Ajouter le remote GitHub
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git

# 3. Renommer la branche en main
git branch -M main

# 4. Pousser TOUT vers GitHub
git push -u origin main
```

**Lors du push, entrez** :
- Username : `votre-username`
- Password : `ghp_votre_token_copié`

**C'EST TOUT !** Tout s'upload en une seule fois.

---

## ✅ Vérification

Après le push réussi, vérifiez sur :

```
https://github.com/VOTRE-USERNAME/pulsai
```

Vous devriez voir :
- ✅ 613 fichiers
- ✅ Dossiers : `backend/`, `src/`, `docker/`, `mcp-server/`, `static/`, etc.
- ✅ Commit : "🎉 Rebranding complet: Open WebUI → Pulsai"
- ✅ README-PULSAI.md affiché

---

## 🎨 BONUS : Personnaliser le Repo

### Ajouter une belle description

Sur GitHub, cliquer **About** (roue dentée) :
- **Description** : `Pulsai - Plateforme AI Assistant avec MCP multi-protocole (HTTPS, npx, Docker)`
- **Topics** : `ai`, `chatbot`, `mcp`, `docker`, `fastapi`, `svelte`
- **Website** : (vide ou votre URL)

---

## ⚡ SCRIPT AUTOMATIQUE (Alternative)

**Si vous préférez un script qui fait tout** :

```powershell
# Exécuter ce script (va vous demander votre username GitHub)
.\init-github.bat
```

Puis après création du repo sur GitHub :

```powershell
.\push-to-github.bat
```

---

## 🐛 Si Problème ?

### Erreur : "remote origin already exists"

```powershell
git remote remove origin
git remote add origin https://github.com/VOTRE-USERNAME/pulsai.git
```

### Erreur : "Authentication failed"

- ✅ Vérifiez que vous utilisez le **TOKEN**, pas votre mot de passe
- ✅ Le token doit avoir le scope `repo`
- ✅ Copiez-collez le token correctement (commence par `ghp_`)

### Erreur : "Repository not found"

- ✅ Vérifiez que le repo est créé sur GitHub
- ✅ Vérifiez l'orthographe de votre username
- ✅ Vérifiez l'URL : `https://github.com/USERNAME/pulsai.git`

### Push très lent ?

C'est normal ! Vous uploadez **613 fichiers** (~50MB+ de code).
**Temps estimé** : 2-5 minutes selon votre connexion.

---

## 📊 Ce qui sera uploadé

**Total** : 613 fichiers

### Structure complète :
```
pulsai/
├── backend/
│   ├── pulsai/          ← Code backend rebrandé
│   ├── pulsai_old/      ← Backup
│   ├── migrations/      ← Migrations DB
│   └── requirements.txt
├── src/
│   ├── lib/
│   │   ├── components/  ← Interface Svelte
│   │   ├── i18n/        ← 58 langues
│   │   └── apis/        ← APIs MCP, etc.
│   └── routes/
├── static/
│   ├── favicon.png
│   ├── splash.png
│   └── icons-pulsa/     ← Nouveaux logos SVG
├── docker/
│   ├── pulsai-backend.Dockerfile
│   └── pulsai-frontend.Dockerfile
├── mcp-server/
│   └── pulsai_mcp/      ← MCP custom server
├── config/
├── docs/
├── kubernetes/
└── [fichiers config]
```

**Taille totale** : ~50-80 MB (sans node_modules, build, data)

---

## 🎉 Après Upload Réussi

Votre équipe pourra :

### Cloner le projet :
```powershell
git clone https://github.com/VOTRE-USERNAME/pulsai.git
cd pulsai
```

### Démarrer Pulsai :
```powershell
# Build et start
docker-compose -f docker-compose.pulsai.yaml up -d

# Accéder
http://localhost:8080
```

### Travailler en équipe :
```powershell
# Pull les dernières modifs
git pull origin main

# Push vos modifs
git add .
git commit -m "Description des modifs"
git push origin main
```

---

## 📝 RÉSUMÉ : 3 Commandes

```powershell
# 1. Ajouter remote (remplacer USERNAME)
git remote add origin https://github.com/USERNAME/pulsai.git

# 2. Branch → main
git branch -M main

# 3. Push TOUT
git push -u origin main
```

**Entrez votre username et TOKEN (pas mot de passe) quand demandé.**

---

**Temps total : 5 minutes max** ⚡

**Questions ? Voir section Troubleshooting ci-dessus** 💡

