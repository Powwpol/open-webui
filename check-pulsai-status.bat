@echo off
REM Script de diagnostic complet Pulsai avec MCP Docker

echo ==================================================
echo    📊 Pulsai Project Status Check
echo ==================================================
echo.

echo 🐳 Docker Containers
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | findstr /V "CONTAINER"
echo.

echo 📦 Pulsai Images
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker images | findstr "pulsai\|open-webui-open-webui"
echo.

echo 💾 Volumes
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker volume ls | findstr "pulsai\|webui"
echo.

echo 🌐 Networks
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker network ls | findstr "pulsai"
echo.

echo 🔍 Health Checks
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo [Ollama]
curl -s http://localhost:11434/api/version 2>nul
if %errorlevel% equ 0 (
    echo ✅ Ollama is running
) else (
    echo ❌ Ollama is not responding
)
echo.

echo [Backend]
curl -s http://localhost:8080/health 2>nul
if %errorlevel% equ 0 (
    echo ✅ Backend is running
) else (
    echo ⚠️  Backend is not running (expected if not started yet)
)
echo.

echo [Redis]
docker exec pulsai-redis redis-cli ping 2>nul
if %errorlevel% equ 0 (
    echo ✅ Redis is running
) else (
    echo ⚠️  Redis is not running
)
echo.

echo [MCP Server]
curl -s http://localhost:8001/health 2>nul
if %errorlevel% equ 0 (
    echo ✅ MCP Server is running
) else (
    echo ⚠️  MCP Server is not running
)
echo.

echo 💡 Build Info
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker inspect open-webui-open-webui:latest --format "{{.Created}} | Size: {{.Size}}" 2>nul
echo.

echo 📊 Resource Usage
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>nul
echo.

echo ==================================================
echo    Recommendations
echo ==================================================
echo.
echo ✅ Your build 'xn3xof' is available as:
echo    → open-webui-open-webui:latest (8.05GB)
echo.
echo 🚀 To integrate it with Pulsai:
echo.
echo    1. Transform the build:
echo       transform-build-to-pulsai.bat
echo.
echo    2. Start the full stack:
echo       start-from-build.bat
echo.
echo    3. Or use docker-compose:
echo       docker-compose -f docker-compose.from-build.yaml up -d
echo.
echo 📖 For more info:
echo    docker-compose -f docker-compose.from-build.yaml logs -f
echo.

pause

