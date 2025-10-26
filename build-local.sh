#!/bin/bash

###############################################################################
# Pulsai Local Build Script
# Build frontend + backend depuis fichiers locaux
###############################################################################

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
USE_SLIM="false"
NO_CACHE=""

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
        *)
            shift
            ;;
    esac
done

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   Pulsai Local Build - Frontend + Backend${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo -e "Configuration:"
echo -e "  Slim: ${GREEN}${USE_SLIM}${NC}"
echo -e "  No Cache: ${GREEN}${NO_CACHE:-false}${NC}"
echo ""

###############################################################################
# Build Backend
###############################################################################

echo -e "${BLUE}Step 1: Building Pulsai Backend (local files)...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker build \
    $NO_CACHE \
    --build-arg USE_SLIM=$USE_SLIM \
    -t pulsai/backend:local \
    -f docker/pulsai-backend.Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend built successfully${NC}"
else
    echo -e "${RED}❌ Backend build failed!${NC}"
    exit 1
fi

echo ""

###############################################################################
# Build Frontend
###############################################################################

echo -e "${BLUE}Step 2: Building Pulsai Frontend (local files)...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker build \
    $NO_CACHE \
    -t pulsai/frontend:local \
    -f docker/pulsai-frontend.Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend built successfully${NC}"
else
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi

echo ""

###############################################################################
# Build MCP Server
###############################################################################

echo -e "${BLUE}Step 3: Building Pulsai MCP Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -d "mcp-server" ]; then
    docker build \
        $NO_CACHE \
        -t pulsai/mcp:local \
        -f mcp-server/Dockerfile \
        mcp-server/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ MCP server built successfully${NC}"
    else
        echo -e "${RED}❌ MCP server build failed!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ MCP server directory not found, skipping${NC}"
fi

echo ""

###############################################################################
# Summary
###############################################################################

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}   ✅ Build Complete!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo "Built images:"
docker images | grep "pulsai.*local"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Start all services:"
echo -e "   ${BLUE}docker-compose -f docker-compose.local-build.yaml up -d${NC}"
echo ""
echo "2. View logs:"
echo -e "   ${BLUE}docker-compose -f docker-compose.local-build.yaml logs -f${NC}"
echo ""
echo "3. Access Pulsai:"
echo -e "   Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "   Backend:  ${BLUE}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"



