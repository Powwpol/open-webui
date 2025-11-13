@echo off
REM ========================================
REM Rebuild Rapide Pulsai depuis GitHub
REM Utilise docker-compose pour build
REM ========================================

echo.
echo ==================================================
echo    🔄 Rebuild Pulsai depuis GitHub
echo ==================================================
echo.

REM Configuration
set GITHUB_REPO=https://github.com/Powwpol/open-webui.git
set COMPOSE_FILE=docker-compose.github.yaml

echo Configuration:
echo   - Source: %GITHUB_REPO%
echo   - Compose: %COMPOSE_FILE%
echo.

REM Vérifier que le fichier compose existe
if not exist %COMPOSE_FILE% (
    echo ❌ Fichier %COMPOSE_FILE% introuvable!
    echo.
    echo Assurez-vous d'être dans le bon dossier.
    pause
    exit /b 1
)

echo ================================================
echo    Étape 1/3: Arrêt des services existants
echo ================================================
echo.

docker-compose -f %COMPOSE_FILE% down
echo ✅ Services arrêtés
echo.

echo ================================================
echo    Étape 2/3: Build depuis GitHub
echo ================================================
echo.
echo ⏳ Build en cours...
echo    (Cela peut prendre 5-10 minutes)
echo.

docker-compose -f %COMPOSE_FILE% build --no-cache

if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo ✅ Images buildées depuis GitHub
echo.

echo ================================================
echo    Étape 3/3: Démarrage des services
echo ================================================
echo.

docker-compose -f %COMPOSE_FILE% up -d

if errorlevel 1 (
    echo.
    echo ❌ Démarrage failed!
    pause
    exit /b 1
)

echo ✅ Services démarrés
echo.

REM ========================================
REM Vérification
REM ========================================

echo ================================================
echo    🔍 Vérification
echo ================================================
echo.

timeout /t 5 >nul

echo Services:
docker-compose -f %COMPOSE_FILE% ps
echo.

echo Images buildées:
docker images | findstr "pulsai.*github"
echo.

REM ========================================
REM Summary
REM ========================================

echo ================================================
echo    ✅ Rebuild Complet!
echo ================================================
echo.
echo 📍 Source: %GITHUB_REPO%
echo 🐳 Images: pulsai/backend:github, pulsai/mcp:github
echo.
echo 🌐 Accès:
echo    - Backend: http://localhost:8080
echo    - MCP: http://localhost:8001
echo    - Ollama: http://localhost:11434
echo.
echo 📊 Logs:
echo    docker-compose -f %COMPOSE_FILE% logs -f
echo.
echo 🛑 Arrêter:
echo    docker-compose -f %COMPOSE_FILE% down
echo.

pause

