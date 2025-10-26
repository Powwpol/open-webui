#!/bin/bash

###############################################################################
# Pulsai Quick Start Script
# 
# One-command setup and launch for Pulsai
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ██╗   ██╗██╗     ███████╗ █████╗ ██╗              ║
║   ██╔══██╗██║   ██║██║     ██╔════╝██╔══██╗██║              ║
║   ██████╔╝██║   ██║██║     ███████╗███████║██║              ║
║   ██╔═══╝ ██║   ██║██║     ╚════██║██╔══██║██║              ║
║   ██║     ╚██████╔╝███████╗███████║██║  ██║██║              ║
║   ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝              ║
║                                                               ║
║              Next-Gen AI Assistant Platform                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found. Please install Docker Compose first.${NC}"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker daemon not running. Please start Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon running${NC}"

echo ""

# Check for existing images
echo -e "${BLUE}Checking for Pulsai images...${NC}"
if docker images | grep -q "pulsai/backend"; then
    echo -e "${GREEN}✓ Pulsai images found${NC}"
    USE_EXISTING="yes"
else
    echo -e "${YELLOW}⚠ Pulsai images not found. Will build them.${NC}"
    USE_EXISTING="no"
fi

echo ""

# Build images if needed
if [ "$USE_EXISTING" = "no" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Building Pulsai images (this may take 10-15 minutes)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ -f "build-pulsai.sh" ]; then
        ./build-pulsai.sh --tag latest
    else
        echo -e "${RED}✗ build-pulsai.sh not found${NC}"
        exit 1
    fi
fi

# Setup configuration
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Setting up configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create config directory
if [ ! -d "config" ]; then
    mkdir -p config
    echo -e "${GREEN}✓ Created config directory${NC}"
fi

# Copy MCP example config if needed
if [ ! -f "config/mcp-servers.yaml" ] && [ -f "config/mcp-servers.yaml.example" ]; then
    cp config/mcp-servers.yaml.example config/mcp-servers.yaml
    echo -e "${GREEN}✓ Created MCP configuration${NC}"
fi

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Creating default .env file${NC}"
    cat > .env << 'ENVEOF'
# Pulsai Configuration
WEBUI_NAME=Pulsai
WEBUI_SECRET_KEY=change-me-to-a-secure-secret-$(openssl rand -hex 32)
ENABLE_SIGNUP=true
ENABLE_WEBHOOKS=true
ANONYMIZED_TELEMETRY=false
LOG_LEVEL=INFO
ENVEOF
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Remember to change WEBUI_SECRET_KEY in .env${NC}"
fi

echo ""

# Start services
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Starting Pulsai services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker-compose -f docker-compose.pulsai.yaml up -d

# Wait for services to be ready
echo ""
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Health checks
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Health checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check backend
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8080/health &> /dev/null; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo -e "${YELLOW}⏳ Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Backend failed to start. Check logs: docker-compose -f docker-compose.pulsai.yaml logs pulsai-backend${NC}"
fi

# Check Redis
if docker-compose -f docker-compose.pulsai.yaml exec -T pulsai-redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Redis check failed${NC}"
fi

# Check MCP
if curl -s http://localhost:8001/health &> /dev/null; then
    echo -e "${GREEN}✓ MCP server is healthy${NC}"
else
    echo -e "${YELLOW}⚠ MCP server check failed${NC}"
fi

# Check Ollama
if curl -s http://localhost:11434/api/version &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Ollama check failed${NC}"
fi

echo ""

# Success message
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✓ Pulsai is ready!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Access Pulsai:${NC}"
echo -e "  🌐 Web Interface: ${BLUE}http://localhost:8080${NC}"
echo -e "  🔌 Backend API:   ${BLUE}http://localhost:8080/api/docs${NC}"
echo -e "  🤖 MCP Server:    ${BLUE}http://localhost:8001${NC}"
echo -e "  🦙 Ollama:        ${BLUE}http://localhost:11434${NC}"
echo ""
echo -e "${CYAN}Useful commands:${NC}"
echo -e "  View logs:        ${BLUE}docker-compose -f docker-compose.pulsai.yaml logs -f${NC}"
echo -e "  Stop services:    ${BLUE}docker-compose -f docker-compose.pulsai.yaml down${NC}"
echo -e "  Restart:          ${BLUE}docker-compose -f docker-compose.pulsai.yaml restart${NC}"
echo -e "  Health check:     ${BLUE}make health${NC}"
echo ""
echo -e "${PURPLE}Documentation:${NC}"
echo -e "  Docker Guide:     ${BLUE}./DOCKER_PULSAI.md${NC}"
echo -e "  MCP Guide:        ${BLUE}./docs/MCP_GUIDE.md${NC}"
echo -e "  Deployment:       ${BLUE}./docs/DEPLOYMENT.md${NC}"
echo ""
echo -e "${GREEN}Happy Pulsai-ing! 🚀${NC}"

