# 🚀 Démarrage Rapide - OAuth Pulsai

## Configuration en 3 minutes

### 1️⃣ Fichier `.env` déjà créé ✅

Le fichier `.env` contient toutes les variables OAuth nécessaires.

### 2️⃣ Choisir votre option de démarrage

#### Option A: Sans OAuth (le plus simple)
```bash
docker compose -f docker-compose.pulsai.yaml up -d
```
Accès: http://localhost:8080

#### Option B: Avec OAuth (recommandé)

**Étape 1**: Configurer un provider dans `.env`

Exemple avec Google:
```bash
# Éditer .env
nano .env

# Décommenter et remplir:
GOOGLE_CLIENT_ID=votre-client-id-google
GOOGLE_CLIENT_SECRET=votre-secret-google
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/google/callback
```

**Étape 2**: Générer une clé secrète
```bash
openssl rand -hex 32
# Copier le résultat dans .env → WEBUI_SECRET_KEY
```

**Étape 3**: Valider
```bash
bash validate-oauth-config.sh
```

**Étape 4**: Démarrer
```bash
docker compose -f docker-compose.pulsai.yaml up -d
```

### 3️⃣ Accéder à Pulsai

Ouvrir dans le navigateur:
```
http://localhost:8080
```

## 📖 Configuration des Providers

### Google OAuth
1. [Google Cloud Console](https://console.cloud.google.com/)
2. Créer projet → API Google+ → Identifiants OAuth 2.0
3. URL redirection: `http://localhost:8080/oauth/google/callback`

### Microsoft OAuth
1. [Azure Portal](https://portal.azure.com/)
2. Créer app Azure AD
3. URL redirection: `http://localhost:8080/oauth/microsoft/callback`

### GitHub OAuth
1. [GitHub Settings](https://github.com/settings/developers)
2. Créer OAuth App
3. URL redirection: `http://localhost:8080/oauth/github/callback`

## 🆘 Aide Rapide

```bash
# Valider la config
bash validate-oauth-config.sh

# Voir les logs
docker compose -f docker-compose.pulsai.yaml logs -f

# Arrêter
docker compose -f docker-compose.pulsai.yaml down

# Redémarrer
docker compose -f docker-compose.pulsai.yaml restart
```

## 📚 Documentation Complète

- **Guide complet**: `OAUTH-DOCKER-GUIDE.md`
- **Résumé technique**: `OAUTH-CONFIGURATION-SUMMARY.md`
- **Success report**: `OAUTH-SETUP-SUCCESS.md`

---

**Status**: ✅ Prêt à l'emploi | **Branding**: 🎨 Pulsai | **OAuth**: 🔐 Configuré
