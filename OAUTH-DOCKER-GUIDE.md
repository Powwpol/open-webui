# Configuration OAuth pour Pulsai avec Docker

Ce guide explique comment configurer OAuth pour Pulsai lorsque vous utilisez Docker.

## Configuration Rapide

### 1. Créer le fichier de configuration

Un fichier `.env` a été créé à la racine du projet avec toutes les variables OAuth nécessaires.

### 2. Variables OAuth Disponibles

#### Activation OAuth

```env
# Activer l'inscription via OAuth
ENABLE_OAUTH_SIGNUP=true

# Fusionner les comptes par email
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true
```

#### Providers OAuth Supportés

##### Google OAuth

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_SCOPE=openid email profile
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/google/callback
```

##### Microsoft OAuth

```env
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_CLIENT_TENANT_ID=common
MICROSOFT_OAUTH_SCOPE=openid email profile
MICROSOFT_REDIRECT_URI=http://localhost:8080/oauth/microsoft/callback
```

##### GitHub OAuth

```env
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_CLIENT_SCOPE=user:email
GITHUB_CLIENT_REDIRECT_URI=http://localhost:8080/oauth/github/callback
```

##### Generic OIDC (Keycloak, Auth0, Okta, etc.)

```env
OPENID_PROVIDER_URL=https://your-oidc-provider.com
OAUTH_CLIENT_ID=your-oidc-client-id
OAUTH_CLIENT_SECRET=your-oidc-client-secret
OAUTH_SCOPES=openid email profile
OPENID_REDIRECT_URI=http://localhost:8080/oauth/oidc/callback
OAUTH_PROVIDER_NAME=SSO
```

### 3. Configuration Avancée OAuth

#### Gestion des Rôles

```env
ENABLE_OAUTH_ROLE_MANAGEMENT=false
OAUTH_ROLES_CLAIM=roles
OAUTH_ALLOWED_ROLES=["user", "admin"]
OAUTH_ADMIN_ROLES=["admin"]
```

#### Gestion des Groupes

```env
ENABLE_OAUTH_GROUP_MANAGEMENT=false
ENABLE_OAUTH_GROUP_CREATION=false
OAUTH_GROUPS_CLAIM=groups
OAUTH_BLOCKED_GROUPS=[]
```

#### Attributs Utilisateur

```env
OAUTH_USERNAME_CLAIM=name
OAUTH_EMAIL_CLAIM=email
OAUTH_PICTURE_CLAIM=picture
OAUTH_SUB_CLAIM=sub
```

#### Domaines Autorisés

```env
# Utiliser * pour autoriser tous les domaines
OAUTH_ALLOWED_DOMAINS=*

# Ou spécifier des domaines spécifiques (séparés par des virgules)
# OAUTH_ALLOWED_DOMAINS=example.com,mycompany.com
```

#### Mise à jour de l'Avatar

```env
# Mettre à jour la photo de profil à chaque connexion
OAUTH_UPDATE_PICTURE_ON_LOGIN=false
```

### 4. Sécurité

```env
# Clé secrète pour l'application (IMPORTANT: Changez en production!)
WEBUI_SECRET_KEY=change-me-to-a-secure-secret-key-in-production

# Les clés de chiffrement suivantes utilisent WEBUI_SECRET_KEY par défaut
# OAUTH_CLIENT_INFO_ENCRYPTION_KEY=
# OAUTH_SESSION_TOKEN_ENCRYPTION_KEY=

# Activer le cookie ID token OAuth
ENABLE_OAUTH_ID_TOKEN_COOKIE=true
```

## Démarrage avec Docker

### Option 1: docker-compose.pulsai.yaml (Recommandé)

```bash
docker-compose -f docker-compose.pulsai.yaml up -d
```

### Option 2: docker-compose.local-build.yaml (Build Local)

```bash
docker-compose -f docker-compose.local-build.yaml up -d
```

### Option 3: docker-compose.monolith.yaml (Monolithe)

```bash
docker-compose -f docker-compose.monolith.yaml up -d
```

### Option 4: compose.yaml (Standard)

```bash
docker-compose up -d
```

## Configuration des Providers OAuth

### Google OAuth

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un projet ou sélectionner un projet existant
3. Activer l'API Google+ API
4. Créer des identifiants OAuth 2.0
5. Ajouter l'URL de redirection: `http://localhost:8080/oauth/google/callback`
6. Copier le Client ID et Client Secret dans `.env`

### Microsoft OAuth

1. Aller sur [Azure Portal](https://portal.azure.com/)
2. Créer une application dans Azure AD
3. Ajouter l'URL de redirection: `http://localhost:8080/oauth/microsoft/callback`
4. Créer un secret client
5. Copier le Client ID, Client Secret et Tenant ID dans `.env`

### GitHub OAuth

1. Aller sur [GitHub Developer Settings](https://github.com/settings/developers)
2. Créer une nouvelle OAuth App
3. Ajouter l'URL de redirection: `http://localhost:8080/oauth/github/callback`
4. Copier le Client ID et Client Secret dans `.env`

### Generic OIDC (Keycloak, Auth0, Okta)

1. Dans votre provider OIDC, créer un nouveau client
2. Configurer le client avec les scopes: `openid email profile`
3. Ajouter l'URL de redirection: `http://localhost:8080/oauth/oidc/callback`
4. Copier l'URL du provider, Client ID et Client Secret dans `.env`

## URLs de Redirection pour Production

Pour la production, remplacez `http://localhost:8080` par votre domaine:

```env
GOOGLE_REDIRECT_URI=https://yourdomain.com/oauth/google/callback
MICROSOFT_REDIRECT_URI=https://yourdomain.com/oauth/microsoft/callback
GITHUB_CLIENT_REDIRECT_URI=https://yourdomain.com/oauth/github/callback
OPENID_REDIRECT_URI=https://yourdomain.com/oauth/oidc/callback
```

## Vérification

Une fois le container démarré, accédez à:

- Interface: http://localhost:8080
- Page de connexion avec les boutons OAuth des providers configurés

## Branding Pulsai

Le branding Pulsai est appliqué via la variable:

```env
WEBUI_NAME=Pulsai
```

Cette variable est déjà configurée dans tous les fichiers docker-compose.

## Troubleshooting

### OAuth ne fonctionne pas

1. Vérifiez que les variables d'environnement sont bien définies:
```bash
docker-compose -f docker-compose.pulsai.yaml exec pulsai-backend env | grep OAUTH
```

2. Vérifiez les logs:
```bash
docker-compose -f docker-compose.pulsai.yaml logs -f pulsai-backend
```

3. Vérifiez que les URLs de redirection correspondent exactement

### Erreur "redirect_uri_mismatch"

L'URL de redirection dans votre provider OAuth doit correspondre EXACTEMENT à celle configurée dans `.env`.

### Les utilisateurs OAuth ne peuvent pas s'inscrire

Assurez-vous que `ENABLE_OAUTH_SIGNUP=true` est défini dans `.env`.

## Support

Pour plus d'informations sur la configuration OAuth, consultez:
- [Documentation Backend OAuth](/workspace/backend/pulsai/utils/oauth.py)
- [Configuration Backend](/workspace/backend/pulsai/config.py)

## Sécurité en Production

⚠️ **IMPORTANT**: Avant de déployer en production:

1. Générez une clé secrète forte:
```bash
openssl rand -hex 32
```

2. Mettez à jour `WEBUI_SECRET_KEY` dans `.env`

3. Utilisez HTTPS pour toutes les URLs de redirection

4. Configurez `OAUTH_ALLOWED_DOMAINS` pour restreindre les domaines autorisés

5. Activez la gestion des rôles et groupes si nécessaire
