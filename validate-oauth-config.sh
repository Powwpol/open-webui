#!/bin/bash

# Script de validation de la configuration OAuth pour Pulsai
# Ce script vérifie que tous les fichiers de configuration sont corrects

echo "======================================"
echo "Validation Configuration OAuth - Pulsai"
echo "======================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
PASSED=0
FAILED=0
WARNINGS=0

# Fonction pour afficher un succès
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

# Fonction pour afficher une erreur
fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

# Fonction pour afficher un avertissement
warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo "1. Vérification des fichiers de configuration..."
echo ""

# Vérifier l'existence du fichier .env
if [ -f ".env" ]; then
    pass "Fichier .env existe"
else
    fail "Fichier .env n'existe pas"
fi

# Vérifier les fichiers docker-compose
for file in "docker-compose.pulsai.yaml" "compose.yaml" "docker-compose.local-build.yaml" "docker-compose.from-build.yaml" "docker-compose.monolith.yaml"; do
    if [ -f "$file" ]; then
        pass "Fichier $file existe"
    else
        fail "Fichier $file n'existe pas"
    fi
done

echo ""
echo "2. Vérification des variables OAuth dans .env..."
echo ""

# Variables OAuth obligatoires
REQUIRED_VARS=(
    "ENABLE_OAUTH_SIGNUP"
    "OAUTH_MERGE_ACCOUNTS_BY_EMAIL"
    "WEBUI_NAME"
    "WEBUI_SECRET_KEY"
)

for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "^${var}=" .env 2>/dev/null; then
        value=$(grep "^${var}=" .env | cut -d'=' -f2)
        if [ -z "$value" ]; then
            warn "Variable $var est définie mais vide"
        else
            pass "Variable $var est définie: $value"
        fi
    else
        fail "Variable $var n'est pas définie dans .env"
    fi
done

echo ""
echo "3. Vérification du branding Pulsai..."
echo ""

# Vérifier que WEBUI_NAME=Pulsai dans les fichiers docker-compose
for file in "docker-compose.pulsai.yaml" "compose.yaml" "docker-compose.local-build.yaml" "docker-compose.from-build.yaml" "docker-compose.monolith.yaml"; do
    if [ -f "$file" ]; then
        if grep -q "WEBUI_NAME=Pulsai" "$file"; then
            pass "Branding Pulsai configuré dans $file"
        else
            fail "Branding Pulsai manquant dans $file"
        fi
    fi
done

echo ""
echo "4. Vérification des fichiers de configuration OAuth optionnels..."
echo ""

# Variables OAuth optionnelles (providers)
OPTIONAL_VARS=(
    "GOOGLE_CLIENT_ID"
    "MICROSOFT_CLIENT_ID"
    "GITHUB_CLIENT_ID"
    "OPENID_PROVIDER_URL"
)

PROVIDER_CONFIGURED=0
for var in "${OPTIONAL_VARS[@]}"; do
    if grep -q "^${var}=" .env 2>/dev/null; then
        value=$(grep "^${var}=" .env | cut -d'=' -f2)
        if [ ! -z "$value" ] && [ "$value" != "your-*" ]; then
            pass "Provider OAuth configuré: $var"
            ((PROVIDER_CONFIGURED++))
        fi
    fi
done

if [ $PROVIDER_CONFIGURED -eq 0 ]; then
    warn "Aucun provider OAuth n'est configuré (optionnel)"
    warn "Pour activer OAuth, décommentez et configurez au moins un provider dans .env"
fi

echo ""
echo "5. Vérification de la sécurité..."
echo ""

# Vérifier que WEBUI_SECRET_KEY n'est pas la valeur par défaut
if grep -q "^WEBUI_SECRET_KEY=change-me" .env 2>/dev/null; then
    warn "WEBUI_SECRET_KEY utilise la valeur par défaut"
    warn "Générez une clé sécurisée avec: openssl rand -hex 32"
else
    pass "WEBUI_SECRET_KEY est configurée"
fi

# Vérifier OAUTH_ALLOWED_DOMAINS
if grep -q "^OAUTH_ALLOWED_DOMAINS=" .env 2>/dev/null; then
    value=$(grep "^OAUTH_ALLOWED_DOMAINS=" .env | cut -d'=' -f2)
    if [ "$value" = "*" ]; then
        warn "OAUTH_ALLOWED_DOMAINS=* (tous les domaines autorisés)"
        warn "Considérez restreindre les domaines en production"
    else
        pass "OAUTH_ALLOWED_DOMAINS est restreint"
    fi
fi

echo ""
echo "6. Vérification des fichiers documentation..."
echo ""

if [ -f "OAUTH-DOCKER-GUIDE.md" ]; then
    pass "Guide OAuth-Docker existe"
else
    fail "Guide OAuth-Docker manquant"
fi

echo ""
echo "======================================"
echo "Résumé de la validation"
echo "======================================"
echo -e "${GREEN}Succès: $PASSED${NC}"
echo -e "${YELLOW}Avertissements: $WARNINGS${NC}"
echo -e "${RED}Échecs: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration OAuth validée avec succès!${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo "1. Configurer au moins un provider OAuth dans .env (Google, Microsoft, GitHub, ou OIDC)"
    echo "2. Générer une clé secrète: openssl rand -hex 32"
    echo "3. Démarrer les services: docker compose -f docker-compose.pulsai.yaml up -d"
    echo "4. Accéder à Pulsai: http://localhost:8080"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Des erreurs ont été détectées. Veuillez les corriger avant de continuer.${NC}"
    echo ""
    exit 1
fi
