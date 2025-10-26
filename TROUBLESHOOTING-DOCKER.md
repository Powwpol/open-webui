# 🔧 Pulsai Docker Troubleshooting

Solutions aux problèmes courants Docker sur Windows avec WSL2.

---

## ⚠️ Erreur I/O lors du build (Input/output error)

**Symptômes:**
```
dpkg: error: unable to create new file: Input/output error
Bus error
DockerDesktop/Wsl/ExecError
```

**Cause:** Disque virtuel WSL2 (docker_data.vhdx) corrompu ou plein.

### Solution Rapide (5 minutes)

```cmd
REM 1. Exécuter le fix automatique
fix-docker-simple.bat

REM 2. Builder version slim (plus rapide, sans embeddings)
build-pulsai.bat --slim

REM 3. Si échec, nettoyer et réessayer
docker system prune -af --volumes
build-pulsai.bat --slim --no-cache
```

### Solution Complète (PowerShell Admin)

```powershell
# Exécuter le script de fix complet
.\fix-docker-wsl.ps1

# Ce script va :
# ✓ Arrêter Docker Desktop
# ✓ Nettoyer le cache Docker
# ✓ Arrêter WSL
# ✓ Compacter le VHDX
# ✓ Créer .wslconfig optimisé
# ✓ Redémarrer Docker
```

---

## 💾 Manque d'espace disque

**Vérifier l'espace:**
```powershell
# Taille du VHDX Docker
Get-Item "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx" | Select-Object Length, FullName

# Espace libre sur C:
Get-PSDrive C | Select-Object Free
```

**Nettoyer:**
```cmd
REM Supprimer containers/images inutilisés
docker system prune -af --volumes

REM Supprimer TOUT (⚠️ perte de données)
docker system prune -af --volumes --all

REM Voir l'utilisation
docker system df
```

**Compacter le VHDX (PowerShell Admin):**
```powershell
# 1. Arrêter WSL
wsl --shutdown

# 2. Compacter
$vhdxPath = "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"
Optimize-VHD -Path $vhdxPath -Mode Full

# 3. Redémarrer Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

---

## 🐌 Build très lent

**Solutions:**

### 1. Utiliser version SLIM (recommandé)
```cmd
REM Build sans les models d'embeddings (2x plus rapide)
build-pulsai.bat --slim
```

### 2. Augmenter ressources WSL2

Créer/éditer `C:\Users\votre-nom\.wslconfig`:

```ini
[wsl2]
memory=8GB          # Augmenter à 8-16GB
processors=4        # Utiliser 4+ CPU cores
swap=4GB            # Augmenter swap
localhostForwarding=true
```

**Appliquer:**
```cmd
wsl --shutdown
REM Redémarrer Docker Desktop
```

### 3. Utiliser cache Docker

```cmd
REM Build normal (utilise le cache)
build-pulsai.bat

REM Build sans cache (lent, mais propre)
build-pulsai.bat --no-cache
```

---

## 🔄 Docker Desktop ne démarre pas

**Étapes:**

1. **Vérifier services Windows:**
   ```cmd
   sc query com.docker.service
   sc query LxssManager
   ```

2. **Redémarrer services:**
   ```cmd
   net stop com.docker.service
   net start com.docker.service
   wsl --shutdown
   ```

3. **Réinitialiser WSL:**
   ```cmd
   wsl --unregister docker-desktop
   wsl --unregister docker-desktop-data
   REM Redémarrer Docker Desktop
   ```

4. **Factory Reset (dernier recours):**
   - Docker Desktop → Troubleshoot → Reset to factory defaults
   - ⚠️ Supprime toutes les images/containers

---

## 🌐 Erreurs réseau lors du build

**Symptômes:**
```
Failed to fetch ...
Could not resolve host
Connection timeout
```

**Solutions:**

### 1. Configurer proxy Docker

Créer/éditer `~/.docker/config.json`:

```json
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy.example.com:8080",
      "httpsProxy": "http://proxy.example.com:8080",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

### 2. Changer DNS Docker

Docker Desktop → Settings → Docker Engine:

```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

### 3. Retry build
```cmd
REM Les packages Pyodide se téléchargent automatiquement
REM Si timeout, juste relancer
build-pulsai.bat
```

---

## 🚫 Permission denied / Access denied

**Solution:**

1. **Exécuter en Admin:**
   ```cmd
   REM Clic droit → Exécuter en tant qu'administrateur
   build-pulsai.bat
   ```

2. **Vérifier partage de lecteur:**
   - Docker Desktop → Settings → Resources → File Sharing
   - Ajouter `C:\Users`

3. **Désactiver antivirus temporairement:**
   - Peut bloquer Docker
   - Ajouter exception pour Docker

---

## 📦 Build réussit mais service ne démarre pas

**Diagnostic:**

```cmd
REM Voir les logs du container
docker-compose -f docker-compose.pulsai.yaml logs pulsai-backend

REM Vérifier les ports
netstat -ano | findstr ":8080"

REM Entrer dans le container
docker-compose -f docker-compose.pulsai.yaml exec pulsai-backend bash
```

**Solutions courantes:**

### Port déjà utilisé
```yaml
# Changer le port dans docker-compose.pulsai.yaml
services:
  pulsai-backend:
    ports:
      - "3000:8080"  # Utiliser 3000 au lieu de 8080
```

### Migration database échouée
```cmd
docker-compose -f docker-compose.pulsai.yaml exec pulsai-backend bash
cd /app/backend
alembic upgrade head
```

### Permissions volumes
```cmd
REM Recréer les volumes
docker-compose -f docker-compose.pulsai.yaml down -v
docker-compose -f docker-compose.pulsai.yaml up -d
```

---

## 🔥 Build bloqué pendant longtemps

**Si bloqué sur:**

### `npm run build` (frontend)
```
#25 42.51 Package threadpoolctl-3.5.0-py3-none-any.whl loaded...
```

- **Normal:** Téléchargement Pyodide packages (3-5 minutes)
- **Si >10 min:** Ctrl+C et relancer

### `pip install` (backend)
```
Collecting package...
```

- **Normal:** Installation deps Python (5-10 minutes)
- **Si >20 min:** Problème réseau, relancer avec `--no-cache`

### `docker build` ne démarre pas

```cmd
REM Vérifier espace disque
docker system df

REM Nettoyer
docker system prune -af

REM Relancer
build-pulsai.bat --slim
```

---

## 💡 Recommandations Générales

### Pour un build rapide et fiable :

```cmd
REM 1. Version SLIM (2x plus rapide)
build-pulsai.bat --slim

REM 2. Vérifier ressources avant build
docker system df
docker system info

REM 3. Nettoyer si nécessaire
docker system prune -af --volumes

REM 4. Builder
build-pulsai.bat --slim --no-cache
```

### Configuration WSL2 optimale :

**`.wslconfig`** (dans `C:\Users\votre-nom\`):
```ini
[wsl2]
memory=8GB
processors=4
swap=4GB
localhostForwarding=true

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```

### Ressources recommandées :

| Build Type | RAM | Disk | Time |
|------------|-----|------|------|
| **Slim** | 4GB | 10GB | 8-12 min |
| **Full** | 8GB | 20GB | 15-20 min |
| **GPU** | 8GB | 30GB | 20-25 min |

---

## 🆘 Encore des problèmes ?

### Logs à vérifier :

1. **Docker Desktop logs:**
   - `%LOCALAPPDATA%\Docker\log.txt`

2. **WSL logs:**
   ```cmd
   wsl --status
   wsl -l -v
   ```

3. **Build logs:**
   ```cmd
   docker-compose -f docker-compose.pulsai.yaml logs -f
   ```

### Reset complet (dernier recours) :

```cmd
REM 1. Sauvegarder données (si nécessaire)
docker cp pulsai-backend:/app/backend/data ./backup

REM 2. Tout supprimer
docker-compose -f docker-compose.pulsai.yaml down -v
docker system prune -af --volumes --all

REM 3. Reset WSL
wsl --shutdown
wsl --unregister docker-desktop
wsl --unregister docker-desktop-data

REM 4. Redémarrer Docker Desktop

REM 5. Rebuild
build-pulsai.bat --slim --no-cache
```

---

## ✅ Build réussi ! Vérifications :

```cmd
REM Vérifier les images
docker images | findstr pulsai

REM Lancer les services
docker-compose -f docker-compose.pulsai.yaml up -d

REM Vérifier la santé
docker-compose -f docker-compose.pulsai.yaml ps

REM Accéder à Pulsai
start http://localhost:8080
```

---

**Besoin d'aide ?**
- **Documentation:** [DOCKER_PULSAI.md](./DOCKER_PULSAI.md)
- **Quick Fix:** `fix-docker-simple.bat`
- **Full Fix:** `fix-docker-wsl.ps1` (PowerShell Admin)

---

**Last Updated:** 19 octobre 2025  
**Pulsai Docker Troubleshooting** 🔧





