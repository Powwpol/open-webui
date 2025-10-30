# ✅ Configuration OAuth pour Pulsai - Docker Ready

Ce document résume la configuration OAuth pour Pulsai, prête pour Docker.

## 📋 Changements Effectués

### 1. Fichier de Configuration `.env`
✅ Créé `/workspace/.env` avec:
- Configuration complète OAuth (tous les providers supportés)
- Variables de sécurité
- Branding Pulsai (`WEBUI_NAME=Pulsai`)
- Configuration Redis, Ollama, Database
- Documentation inline complète

### 2. Fichiers Docker Compose Mis à Jour
✅ Tous les fichiers docker-compose incluent maintenant:
- `env_file: .env` pour charger les variables OAuth
- `WEBUI_NAME=Pulsai` pour le branding
- Configuration OAuth activée

Fichiers modifiés:
- ✅ `docker-compose.pulsai.yaml`
- ✅ `compose.yaml`
- ✅ `docker-compose.local-build.yaml`
- ✅ `docker-compose.from-build.yaml`
- ✅ `docker-compose.monolith.yaml`

### 3. Documentation
✅ Créé `OAUTH-DOCKER-GUIDE.md`:
- Guide complet de configuration OAuth
- Instructions pour chaque provider (Google, Microsoft, GitHub, OIDC)
- Configuration avancée (rôles, groupes, domaines)
- Troubleshooting

### 4. Script de Validation
✅ Créé `validate-oauth-config.sh`:
- Valide la configuration OAuth
- Vérifie le branding Pulsai
- Détecte les problèmes de sécurité
- Affiche un rapport complet

## 🚀 Démarrage Rapide

### Option 1: Configuration Minimale (Sans OAuth)

```bash
# 1. Le fichier .env est déjà créé avec les valeurs par défaut
# 2. Démarrer les services
docker compose -f docker-compose.pulsai.yaml up -d

# 3. Accéder à Pulsai
open http://localhost:8080
```

### Option 2: Avec OAuth (Recommandé)

```bash
# 1. Éditer le fichier .env et décommenter/configurer un provider
nano .env

# Exemple pour Google OAuth:
# GOOGLE_CLIENT_ID=votre-client-id
# GOOGLE_CLIENT_SECRET=votre-client-secret
# GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/google/callback

# 2. Générer une clé secrète sécurisée
openssl rand -hex 32
# Copier le résultat dans .env pour WEBUI_SECRET_KEY

# 3. Valider la configuration
bash validate-oauth-config.sh

# 4. Démarrer les services
docker compose -f docker-compose.pulsai.yaml up -d

# 5. Accéder à Pulsai
open http://localhost:8080
```

## 📝 Configuration des Providers OAuth

### Google OAuth
1. [Console Google Cloud](https://console.cloud.google.com/)
2. Créer un projet → Activer Google+ API
3. Créer des identifiants OAuth 2.0
4. URL de redirection: `http://localhost:8080/oauth/google/callback`

### Microsoft OAuth
1. [Azure Portal](https://portal.azure.com/)
2. Créer une application Azure AD
3. URL de redirection: `http://localhost:8080/oauth/microsoft/callback`

### GitHub OAuth
1. [GitHub Developer Settings](https://github.com/settings/developers)
2. Créer une OAuth App
3. URL de redirection: `http://localhost:8080/oauth/github/callback`

### Generic OIDC (Keycloak, Auth0, Okta)
1. Créer un client dans votre provider
2. Scopes: `openid email profile`
3. URL de redirection: `http://localhost:8080/oauth/oidc/callback`

## 🔍 Validation

Exécutez le script de validation:

```bash
bash validate-oauth-config.sh
```

Résultats attendus:
- ✅ 16+ succès
- ⚠️ 6 avertissements (normaux si OAuth non configuré)
- ❌ 0 échecs

## 🎨 Branding Pulsai

Le branding Pulsai est automatiquement appliqué via:
- `WEBUI_NAME=Pulsai` dans tous les docker-compose
- Variable chargée depuis `.env`
- Visible dans l'interface web

## 📚 Documentation Complète

- **Guide OAuth détaillé**: [`OAUTH-DOCKER-GUIDE.md`](./OAUTH-DOCKER-GUIDE.md)
- **Configuration Backend**: [`backend/pulsai/config.py`](./backend/pulsai/config.py)
- **Implémentation OAuth**: [`backend/pulsai/utils/oauth.py`](./backend/pulsai/utils/oauth.py)

## 🔐 Sécurité Production

⚠️ **Avant de déployer en production**:

1. ✅ Générer une clé secrète forte:
```bash
openssl rand -hex 32
```

2. ✅ Mettre à jour `WEBUI_SECRET_KEY` dans `.env`

3. ✅ Utiliser HTTPS pour toutes les URLs de redirection

4. ✅ Configurer `OAUTH_ALLOWED_DOMAINS` pour restreindre les domaines:
```env
OAUTH_ALLOWED_DOMAINS=votredomaine.com,autredomaine.com
```

5. ✅ Activer la gestion des rôles/groupes si nécessaire:
```env
ENABLE_OAUTH_ROLE_MANAGEMENT=true
OAUTH_ALLOWED_ROLES=["user", "admin"]
```

## 🐛 Troubleshooting

### OAuth ne fonctionne pas
```bash
# Vérifier les variables d'environnement
docker compose -f docker-compose.pulsai.yaml exec pulsai-backend env | grep OAUTH

# Vérifier les logs
docker compose -f docker-compose.pulsai.yaml logs -f pulsai-backend
```

### Erreur "redirect_uri_mismatch"
- Vérifier que l'URL de redirection dans votre provider OAuth correspond EXACTEMENT à celle dans `.env`

### Les utilisateurs OAuth ne peuvent pas s'inscrire
- Vérifier que `ENABLE_OAUTH_SIGNUP=true` dans `.env`

## ✨ Features OAuth Configurées

- ✅ **Inscription via OAuth** (`ENABLE_OAUTH_SIGNUP=true`)
- ✅ **Fusion de comptes par email** (`OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true`)
- ✅ **Cookie ID Token** (`ENABLE_OAUTH_ID_TOKEN_COOKIE=true`)
- ⚪ **Gestion des rôles** (disponible, désactivé par défaut)
- ⚪ **Gestion des groupes** (disponible, désactivé par défaut)
- ⚪ **Mise à jour avatar** (disponible, désactivé par défaut)

## 🎯 Prochaines Étapes

1. ✅ Configuration OAuth créée et validée
2. 🔲 Configurer un provider OAuth dans `.env`
3. 🔲 Générer une clé secrète sécurisée
4. 🔲 Démarrer les services Docker
5. 🔲 Tester la connexion OAuth

## 📞 Support

- Documentation: [`OAUTH-DOCKER-GUIDE.md`](./OAUTH-DOCKER-GUIDE.md)
- Validation: `bash validate-oauth-config.sh`
- Logs: `docker compose -f docker-compose.pulsai.yaml logs -f`

---

**Status**: ✅ Prêt pour Docker | 🎨 Branding Pulsai appliqué | 🔐 OAuth configuré

**Dernière mise à jour**: 2025-10-30
