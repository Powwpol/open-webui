#!/bin/bash

###############################################################################
# Pulsai Docker Build Script
# 
# Builds all Pulsai Docker images:
# - pulsai/backend: FastAPI backend with all features
# - pulsai/mcp: Custom MCP server
#
# Usage:
#   ./build-pulsai.sh [options]
#
# Options:
#   --cuda          Build with CUDA support
#   --gpu           Build with GPU support (alias for --cuda)
#   --slim          Build slim version (no embedding models)
#   --no-cache      Build without Docker cache
#   --push          Push images to registry after build
#   --tag <tag>     Custom tag (default: latest)
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
USE_CUDA="false"
USE_SLIM="false"
NO_CACHE=""
PUSH="false"
TAG="latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --cuda|--gpu)
            USE_CUDA="true"
            shift
            ;;
        --slim)
            USE_SLIM="true"
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --push)
            PUSH="true"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        -h|--help)
            echo "Pulsai Docker Build Script"
            echo ""
            echo "Usage: ./build-pulsai.sh [options]"
            echo ""
            echo "Options:"
            echo "  --cuda, --gpu    Build with CUDA/GPU support"
            echo "  --slim           Build slim version (no models)"
            echo "  --no-cache       Build without Docker cache"
            echo "  --push           Push to registry after build"
            echo "  --tag <tag>      Custom tag (default: latest)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Print build configuration
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Pulsai Docker Build Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "Tag:        ${GREEN}${TAG}${NC}"
echo -e "CUDA:       ${GREEN}${USE_CUDA}${NC}"
echo -e "Slim:       ${GREEN}${USE_SLIM}${NC}"
echo -e "No Cache:   ${GREEN}${NO_CACHE:-false}${NC}"
echo -e "Push:       ${GREEN}${PUSH}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Build hash (git commit or timestamp)
if command -v git &> /dev/null && [ -d .git ]; then
    BUILD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "dev-build")
else
    BUILD_HASH="dev-build-$(date +%Y%m%d)"
fi

echo -e "${YELLOW}Build Hash: ${BUILD_HASH}${NC}"
echo ""

###############################################################################
# Build Pulsai Backend
###############################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Building Pulsai Backend (pulsai/backend:${TAG})${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker build \
    $NO_CACHE \
    --build-arg USE_CUDA=$USE_CUDA \
    --build-arg USE_SLIM=$USE_SLIM \
    --build-arg BUILD_HASH=$BUILD_HASH \
    -t pulsai/backend:$TAG \
    -f Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
else
    echo -e "${RED}✗ Backend build failed${NC}"
    exit 1
fi

# Also tag as 'latest' if building a specific version
if [ "$TAG" != "latest" ]; then
    docker tag pulsai/backend:$TAG pulsai/backend:latest
    echo -e "${GREEN}✓ Tagged as pulsai/backend:latest${NC}"
fi

echo ""

###############################################################################
# Build Pulsai MCP Server
###############################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Building Pulsai MCP Server (pulsai/mcp:${TAG})${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -d "mcp-server" ]; then
    docker build \
        $NO_CACHE \
        -t pulsai/mcp:$TAG \
        -f mcp-server/Dockerfile \
        mcp-server/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ MCP server image built successfully${NC}"
        
        if [ "$TAG" != "latest" ]; then
            docker tag pulsai/mcp:$TAG pulsai/mcp:latest
            echo -e "${GREEN}✓ Tagged as pulsai/mcp:latest${NC}"
        fi
    else
        echo -e "${RED}✗ MCP server build failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ MCP server directory not found, skipping${NC}"
fi

echo ""

###############################################################################
# Summary
###############################################################################

echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✓ Build Complete${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "Built images:"
docker images | grep -E "pulsai/(backend|mcp)" | head -4
echo ""

###############################################################################
# Push to registry (optional)
###############################################################################

if [ "$PUSH" = "true" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Pushing images to registry${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    docker push pulsai/backend:$TAG
    docker push pulsai/mcp:$TAG
    
    if [ "$TAG" != "latest" ]; then
        docker push pulsai/backend:latest
        docker push pulsai/mcp:latest
    fi
    
    echo -e "${GREEN}✓ Images pushed successfully${NC}"
    echo ""
fi

###############################################################################
# Next steps
###############################################################################

echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Run Pulsai with Docker Compose:"
echo -e "   ${BLUE}docker-compose -f docker-compose.pulsai.yaml up -d${NC}"
echo ""
echo "2. Or run backend standalone:"
echo -e "   ${BLUE}docker run -d -p 8080:8080 -v pulsai-data:/app/backend/data pulsai/backend:${TAG}${NC}"
echo ""
echo "3. Check logs:"
echo -e "   ${BLUE}docker-compose -f docker-compose.pulsai.yaml logs -f${NC}"
echo ""
echo "4. Access Pulsai:"
echo -e "   ${BLUE}http://localhost:8080${NC}"
echo ""

echo -e "${GREEN}Happy Pulsai-ing! 🚀${NC}"

