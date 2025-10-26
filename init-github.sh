#!/bin/bash

###############################################################################
# Script d'initialisation GitHub pour Pulsai
# Usage: ./init-github.sh [votre-username-github]
###############################################################################

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
GITHUB_USER=${1:-}

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   🚀 Initialisation GitHub - Pulsai${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Demander le username si pas fourni
if [ -z "$GITHUB_USER" ]; then
    read -p "Entrez votre username GitHub: " GITHUB_USER
fi

echo -e "Configuration:"
echo -e "  - Username GitHub: ${GREEN}${GITHUB_USER}${NC}"
echo -e "  - Repo name: ${GREEN}pulsai${NC}"
echo ""

# Vérifier Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git n'est pas installé!${NC}"
    echo ""
    echo "Installez Git: https://git-scm.com/downloads"
    exit 1
fi

echo -e "${GREEN}✅ Git installé${NC}"
echo ""

###############################################################################
# Étape 1: Vérifier l'état Git
###############################################################################

echo -e "${BLUE}Étape 1: Vérification du dépôt local...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -d .git ]; then
    echo -e "${YELLOW}📦 Initialisation du dépôt Git...${NC}"
    git init
    echo -e "${GREEN}✅ Dépôt Git initialisé${NC}"
else
    echo -e "${GREEN}✅ Dépôt Git déjà initialisé${NC}"
fi
echo ""

###############################################################################
# Étape 2: Nettoyer les anciens remotes
###############################################################################

echo -e "${BLUE}Étape 2: Nettoyage des remotes existants...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

git remote remove origin 2>/dev/null || true
git remote remove upstream 2>/dev/null || true
echo -e "${GREEN}✅ Remotes nettoyés${NC}"
echo ""

###############################################################################
# Étape 3: Configurer le nouveau remote
###############################################################################

echo -e "${BLUE}Étape 3: Configuration du remote GitHub...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

REPO_URL="https://github.com/${GITHUB_USER}/pulsai.git"
echo -e "Ajout remote: ${YELLOW}${REPO_URL}${NC}"
git remote add origin "$REPO_URL"
echo -e "${GREEN}✅ Remote ajouté${NC}"
echo ""

###############################################################################
# Étape 4: Vérifier .gitignore
###############################################################################

echo -e "${BLUE}Étape 4: Vérification .gitignore...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f .gitignore ]; then
    echo -e "${GREEN}✅ .gitignore existe${NC}"
    if grep -q ".env" .gitignore; then
        echo -e "${GREEN}✅ .env ignoré${NC}"
    else
        echo -e "${YELLOW}⚠️  Attention: .env pas dans .gitignore${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .gitignore manquant${NC}"
fi
echo ""

###############################################################################
# Étape 5: Ajouter tous les fichiers
###############################################################################

echo -e "${BLUE}Étape 5: Ajout des fichiers...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

git add .
echo -e "${GREEN}✅ Fichiers ajoutés au staging${NC}"
echo ""

# Afficher un aperçu
echo "Aperçu des fichiers à commiter:"
git status --short | head -20
total_files=$(git status --short | wc -l)
if [ $total_files -gt 20 ]; then
    echo "... et $((total_files - 20)) autres fichiers"
fi
echo ""

###############################################################################
# Étape 6: Créer le commit initial
###############################################################################

echo -e "${BLUE}Étape 6: Création du commit initial...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

git commit -m "🎉 Initial commit: Pulsai rebrandé (fork Open WebUI)" \
    -m "" \
    -m "- Rebranding complet Open WebUI → Pulsai" \
    -m "- 102 fichiers modifiés, ~822 occurrences remplacées" \
    -m "- Configuration MCP complète (HTTPS, npx, Docker, WebSocket, SSE)" \
    -m "- Support 4 utilisateurs en local" \
    -m "- Charte graphique Pulsai appliquée" \
    -m "- Interface en français" \
    -m "" \
    -m "Basé sur Open WebUI v0.6.32" \
    -m "Conforme licence Open WebUI (clause 5.i: <50 utilisateurs)"

echo -e "${GREEN}✅ Commit créé${NC}"
echo ""

###############################################################################
# Instructions finales
###############################################################################

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}   ✅ Repo Git Préparé!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "${YELLOW}📋 PROCHAINES ÉTAPES:${NC}"
echo ""
echo -e "1. Créer le repo sur GitHub:"
echo -e "   ${BLUE}https://github.com/new${NC}"
echo ""
echo "   Repository name: pulsai"
echo "   Visibility: Private (recommandé)"
echo "   ❌ Ne PAS initialiser avec README/License/.gitignore"
echo ""
echo -e "2. Une fois créé sur GitHub, exécuter:"
echo ""
echo -e "   ${BLUE}git branch -M main${NC}"
echo -e "   ${BLUE}git push -u origin main${NC}"
echo ""
echo -e "3. Si demande d'authentification:"
echo -e "   - Username: ${GREEN}${GITHUB_USER}${NC}"
echo "   - Password: Utilisez un Personal Access Token"
echo -e "     (Créer sur: ${BLUE}https://github.com/settings/tokens${NC})"
echo ""
echo -e "4. Vérifier sur:"
echo -e "   ${BLUE}https://github.com/${GITHUB_USER}/pulsai${NC}"
echo ""
echo -e "${GREEN}==================================================${NC}"
echo ""

