@echo off
REM Démarrer Pulsai avec le build existant (xn3xof)

echo ==================================================
echo    Pulsai - Démarrage depuis Build Existant
echo ==================================================
echo.

REM Etape 1: Nettoyer les conteneurs arrêtés
echo Step 1: Cleaning stopped containers...
docker container prune -f >nul 2>&1
echo ✅ Cleanup done
echo.

REM Etape 2: Tag l'image si pas déjà fait
echo Step 2: Tagging image...
docker tag open-webui-open-webui:latest pulsai/backend:from-build 2>nul
echo ✅ Image ready
echo.

REM Etape 3: Connecter pulsai-ollama au réseau pulsai-network (si pas déjà fait)
echo Step 3: Ensuring Ollama is on pulsai-network...
docker network connect pulsai-network pulsai-ollama 2>nul
echo ✅ Network configured
echo.

REM Etape 4: Démarrer les services
echo Step 4: Starting Pulsai stack...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker-compose -f docker-compose.from-build.yaml up -d

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to start services!
    exit /b 1
)

echo.
echo ✅ Services started successfully
echo.

REM Etape 5: Attendre que les services soient prêts
echo Step 5: Waiting for services to be ready...
timeout /t 10 >nul
echo.

REM Etape 6: Vérifier le statut
echo Step 6: Checking service status...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker-compose -f docker-compose.from-build.yaml ps
echo.

REM Etape 7: Health checks
echo Step 7: Health checks...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Backend:
curl -s http://localhost:8080/health 2>nul || echo ⏳ Backend still starting...
echo.
echo Redis:
docker-compose -f docker-compose.from-build.yaml exec -T pulsai-redis redis-cli ping 2>nul || echo ⏳ Redis still starting...
echo.
echo MCP:
curl -s http://localhost:8001/health 2>nul || echo ⏳ MCP still starting...
echo.
echo Ollama:
curl -s http://localhost:11434/api/version 2>nul || echo ⏳ Ollama still starting...
echo.

echo ==================================================
echo    ✅ Pulsai Started!
echo ==================================================
echo.
echo Services:
echo   Backend:  http://localhost:8080
echo   MCP:      http://localhost:8001
echo   Ollama:   http://localhost:11434
echo.
echo Commands:
echo   View logs:     docker-compose -f docker-compose.from-build.yaml logs -f
echo   Stop all:      docker-compose -f docker-compose.from-build.yaml down
echo   Restart:       docker-compose -f docker-compose.from-build.yaml restart
echo.
echo To see live logs:
echo   docker-compose -f docker-compose.from-build.yaml logs -f pulsai-backend
echo.

