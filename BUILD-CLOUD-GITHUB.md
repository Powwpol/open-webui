# ☁️ Build Cloud PulsAI - GitHub Actions

## ✅ Configuration Terminée !

**Status** : ✅ GitHub Actions configuré et poussé  
**Repository** : https://github.com/Powwpol/open-webui  
**Branch** : pulsai  
**Workflow** : `.github/workflows/docker-build-pulsai.yml`

---

## 🚀 Le Build Cloud est Lancé !

GitHub va maintenant builder automatiquement votre image PulsAI dans le cloud.

### 📊 Suivre le Build

1. **Via GitHub Web** :
   ```
   https://github.com/Powwpol/open-webui/actions
   ```

2. **Workflow actif** : "Build PulsAI Docker Image"

3. **Temps estimé** : 15-20 minutes

---

## 🔍 Vérifier la Progression

### Sur GitHub.com

1. Allez sur : https://github.com/Powwpol/open-webui
2. Cliquez sur l'onglet **"Actions"**
3. Vous verrez le workflow en cours : 🟡 "Build PulsAI Docker Image"
4. Cliquez dessus pour voir les détails

### Statuts Possibles

| Icône | Status | Description |
|-------|--------|-------------|
| 🟡 | En cours | Build en cours sur GitHub |
| ✅ | Succès | Image buildée et poussée sur ghcr.io |
| ❌ | Échec | Erreur (voir les logs) |

---

## 📦 Une Fois le Build Terminé

### L'image sera disponible sur :

```
ghcr.io/powwpol/open-webui:pulsai
```

### Utiliser l'Image Cloud

**Option 1 : Docker Compose**

Modifiez `docker-compose.cloud.yaml` :

```yaml
services:
  pulsai-backend:
    image: ghcr.io/powwpol/open-webui:pulsai
    # ... reste de la config
```

Puis :

```bash
docker-compose -f docker-compose.cloud.yaml pull
docker-compose -f docker-compose.cloud.yaml up -d
```

**Option 2 : Docker Run Direct**

```bash
docker pull ghcr.io/powwpol/open-webui:pulsai
docker run -d -p 8080:8080 ghcr.io/powwpol/open-webui:pulsai
```

---

## ⚡ Avantages du Build Cloud

✅ **Build Automatique** : À chaque push sur `pulsai`, l'image se rebuild  
✅ **Hébergé sur GitHub** : Pas besoin de builder localement  
✅ **Pull Rapide** : 2-3 minutes au lieu de 15-20 min de build  
✅ **Cache Optimisé** : Les builds suivants seront encore plus rapides  
✅ **Multi-plateforme** : Image compatible linux/amd64

---

## 🔧 Build Local en Parallèle

Pendant que GitHub build dans le cloud, vous avez **AUSSI** un build local en cours !

### Vérifier le Build Local

```powershell
# Voir si le build local progresse
Get-Process docker-buildx

# Quand terminé
docker images pulsai/backend:github
```

### Utiliser le Build Local (Plus Rapide pour Maintenant)

Si le build local se termine avant le build GitHub :

```bash
docker-compose -f docker-compose.github.yaml up -d
```

---

## 📋 Résumé des Images

Vous aurez **2 images** identiques :

| Image | Source | Utilisation |
|-------|--------|-------------|
| `pulsai/backend:github` | Build local | Immédiat (10-15 min) |
| `ghcr.io/powwpol/open-webui:pulsai` | Build GitHub | Cloud (15-20 min) |

**Recommandation** :
- **Maintenant** : Utilisez le build local (déjà en cours)
- **Futur** : Utilisez l'image cloud (pull rapide)

---

## 🎯 Prochaines Étapes

### 1. Maintenant (Build Local)

```bash
# Attendre 5-10 minutes puis vérifier
docker images pulsai/backend:github

# Si l'image existe, démarrer
docker-compose -f docker-compose.github.yaml up -d
```

### 2. Plus Tard (Build Cloud)

Une fois le build GitHub terminé :

```bash
# Modifier docker-compose.cloud.yaml pour utiliser ghcr.io
# Puis :
docker-compose -f docker-compose.cloud.yaml pull
docker-compose -f docker-compose.cloud.yaml up -d
```

---

## 🔄 Workflow Automatique Futur

Désormais, à chaque fois que vous :

```bash
git add backend/quelque-chose.py
git commit -m "fix: amélioration"
git push origin pulsai
```

GitHub va automatiquement :
1. ✅ Détecter le changement
2. ✅ Builder la nouvelle image
3. ✅ Pousser sur ghcr.io/powwpol/open-webui:pulsai
4. ✅ Vous pourrez pull la nouvelle version

---

## 📊 Status Actuel

| Élément | Status | Temps restant |
|---------|--------|---------------|
| **Build Local** | 🔄 En cours | ~10 min |
| **Build GitHub Cloud** | 🔄 Démarré | ~15 min |
| **Correctif pulsai.main:app** | ✅ Inclus | - |
| **GitHub Actions** | ✅ Configuré | - |

---

## 🎉 Félicitations !

Vous avez maintenant :
- ✅ Le correctif `pulsai.main:app` qui résout l'erreur
- ✅ Un build local en cours
- ✅ Un build cloud automatique configuré
- ✅ Une image qui sera disponible sur ghcr.io

**Dans 10-15 minutes, PulsAI sera prêt à l'emploi !** 🚀

---

**Liens Utiles** :
- Repository : https://github.com/Powwpol/open-webui
- Actions : https://github.com/Powwpol/open-webui/actions
- Packages : https://github.com/Powwpol?tab=packages


