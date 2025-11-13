@echo off
REM ========================================
REM Build Pulsai depuis GitHub
REM Source: https://github.com/Powwpol/open-webui
REM ========================================

echo.
echo ==================================================
echo    🐳 Build Pulsai depuis GitHub
echo ==================================================
echo.

REM Configuration
set GITHUB_REPO=https://github.com/Powwpol/open-webui.git
set BRANCH=main
set USE_SLIM=false
set NO_CACHE=
set TAG=latest

REM Parse arguments
:parse_args
if "%~1"=="" goto :end_parse
if /i "%~1"=="--slim" (
    set USE_SLIM=true
    shift
    goto :parse_args
)
if /i "%~1"=="--no-cache" (
    set NO_CACHE=--no-cache
    shift
    goto :parse_args
)
if /i "%~1"=="--tag" (
    set TAG=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--branch" (
    set BRANCH=%~2
    shift
    shift
    goto :parse_args
)
shift
goto :parse_args

:end_parse

echo Configuration:
echo   - Repo GitHub: %GITHUB_REPO%
echo   - Branch: %BRANCH%
echo   - Slim: %USE_SLIM%
echo   - Tag: %TAG%
echo   - No Cache: %NO_CACHE%
echo.

REM ========================================
REM Étape 1: Clone ou Pull du repo
REM ========================================

echo ================================================
echo    Étape 1/3: Récupération du code GitHub
echo ================================================
echo.

if exist .git (
    echo 📥 Mise à jour depuis GitHub...
    git fetch origin
    git reset --hard origin/%BRANCH%
    git pull origin %BRANCH%
    echo ✅ Code mis à jour
) else (
    echo 📦 Clonage du repository...
    git clone -b %BRANCH% %GITHUB_REPO% .
    echo ✅ Repository cloné
)
echo.

REM ========================================
REM Étape 2: Build Backend
REM ========================================

echo ================================================
echo    Étape 2/3: Build Backend Pulsai
echo ================================================
echo.

docker build ^
    %NO_CACHE% ^
    --build-arg USE_SLIM=%USE_SLIM% ^
    -t pulsai/backend:%TAG% ^
    -f Dockerfile ^
    .

if errorlevel 1 (
    echo.
    echo ❌ Backend build failed!
    pause
    exit /b 1
)

echo ✅ Backend built: pulsai/backend:%TAG%
echo.

REM ========================================
REM Étape 3: Build MCP Server
REM ========================================

echo ================================================
echo    Étape 3/3: Build MCP Server
echo ================================================
echo.

if exist mcp-server (
    docker build ^
        %NO_CACHE% ^
        -t pulsai/mcp:%TAG% ^
        -f mcp-server/Dockerfile ^
        mcp-server/
    
    if errorlevel 1 (
        echo.
        echo ❌ MCP build failed!
        pause
        exit /b 1
    )
    
    echo ✅ MCP built: pulsai/mcp:%TAG%
) else (
    echo ⚠️ MCP server directory not found
)
echo.

REM ========================================
REM Summary
REM ========================================

echo ================================================
echo    ✅ Build Complet depuis GitHub!
echo ================================================
echo.
echo Built images:
docker images | findstr "pulsai.*%TAG%"
echo.
echo 📍 Source: %GITHUB_REPO%
echo 🌿 Branch: %BRANCH%
echo.
echo 🚀 Next steps:
echo.
echo 1. Start Pulsai:
echo    docker-compose -f docker-compose.pulsai.yaml up -d
echo.
echo 2. View logs:
echo    docker-compose -f docker-compose.pulsai.yaml logs -f
echo.
echo 3. Access Pulsai:
echo    http://localhost:8080
echo.
echo ================================================
echo.

pause

