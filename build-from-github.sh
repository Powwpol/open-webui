#!/bin/bash

###############################################################################
# Build Pulsai depuis GitHub
# Source: https://github.com/Powwpol/open-webui
###############################################################################

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
GITHUB_REPO="https://github.com/Powwpol/open-webui.git"
BRANCH="main"
USE_SLIM="false"
NO_CACHE=""
TAG="latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --slim)
            USE_SLIM="true"
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   🐳 Build Pulsai depuis GitHub${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo -e "Configuration:"
echo -e "  - Repo GitHub: ${GREEN}${GITHUB_REPO}${NC}"
echo -e "  - Branch: ${GREEN}${BRANCH}${NC}"
echo -e "  - Slim: ${GREEN}${USE_SLIM}${NC}"
echo -e "  - Tag: ${GREEN}${TAG}${NC}"
echo -e "  - No Cache: ${GREEN}${NO_CACHE:-false}${NC}"
echo ""

###############################################################################
# Étape 1: Clone ou Pull du repo
###############################################################################

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Étape 1/3: Récupération du code GitHub${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

if [ -d .git ]; then
    echo -e "${YELLOW}📥 Mise à jour depuis GitHub...${NC}"
    git fetch origin
    git reset --hard origin/${BRANCH}
    git pull origin ${BRANCH}
    echo -e "${GREEN}✅ Code mis à jour${NC}"
else
    echo -e "${YELLOW}📦 Clonage du repository...${NC}"
    git clone -b ${BRANCH} ${GITHUB_REPO} .
    echo -e "${GREEN}✅ Repository cloné${NC}"
fi
echo ""

###############################################################################
# Étape 2: Build Backend
###############################################################################

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Étape 2/3: Build Backend Pulsai${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

docker build \
    $NO_CACHE \
    --build-arg USE_SLIM=$USE_SLIM \
    -t pulsai/backend:$TAG \
    -f Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend built: pulsai/backend:${TAG}${NC}"
else
    echo -e "${RED}❌ Backend build failed!${NC}"
    exit 1
fi
echo ""

###############################################################################
# Étape 3: Build MCP Server
###############################################################################

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Étape 3/3: Build MCP Server${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

if [ -d "mcp-server" ]; then
    docker build \
        $NO_CACHE \
        -t pulsai/mcp:$TAG \
        -f mcp-server/Dockerfile \
        mcp-server/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ MCP built: pulsai/mcp:${TAG}${NC}"
    else
        echo -e "${RED}❌ MCP build failed!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ MCP server directory not found${NC}"
fi
echo ""

###############################################################################
# Summary
###############################################################################

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   ✅ Build Complet depuis GitHub!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Built images:"
docker images | grep "pulsai.*${TAG}"
echo ""
echo -e "${YELLOW}📍 Source: ${GITHUB_REPO}${NC}"
echo -e "${YELLOW}🌿 Branch: ${BRANCH}${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo ""
echo "1. Start Pulsai:"
echo -e "   ${GREEN}docker-compose -f docker-compose.pulsai.yaml up -d${NC}"
echo ""
echo "2. View logs:"
echo -e "   ${GREEN}docker-compose -f docker-compose.pulsai.yaml logs -f${NC}"
echo ""
echo "3. Access Pulsai:"
echo -e "   ${GREEN}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}================================================${NC}"
echo ""

