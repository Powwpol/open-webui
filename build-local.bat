@echo off
REM Pulsai Local Build Script for Windows
REM Build frontend + backend depuis fichiers locaux

echo ==================================================
echo    Pulsai Local Build - Frontend + Backend
echo ==================================================
echo.

REM Parse arguments
set USE_SLIM=false
set NO_CACHE=

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
shift
goto :parse_args

:end_parse

echo Configuration:
echo   Slim: %USE_SLIM%
echo   No Cache: %NO_CACHE%
echo.

echo Step 1: Building Pulsai Backend (local files)...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

docker build ^
    %NO_CACHE% ^
    --build-arg USE_SLIM=%USE_SLIM% ^
    -t pulsai/backend:local ^
    -f docker/pulsai-backend.Dockerfile ^
    .

if errorlevel 1 (
    echo.
    echo ❌ Backend build failed!
    exit /b 1
)

echo ✅ Backend built successfully
echo.

echo Step 2: Building Pulsai Frontend (local files)...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

docker build ^
    %NO_CACHE% ^
    -t pulsai/frontend:local ^
    -f docker/pulsai-frontend.Dockerfile ^
    .

if errorlevel 1 (
    echo.
    echo ❌ Frontend build failed!
    exit /b 1
)

echo ✅ Frontend built successfully
echo.

echo Step 3: Building Pulsai MCP Server...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if exist mcp-server (
    docker build ^
        %NO_CACHE% ^
        -t pulsai/mcp:local ^
        -f mcp-server/Dockerfile ^
        mcp-server/
    
    if errorlevel 1 (
        echo.
        echo ❌ MCP server build failed!
        exit /b 1
    )
    
    echo ✅ MCP server built successfully
) else (
    echo ⚠ MCP server directory not found, skipping
)

echo.
echo ==================================================
echo    ✅ Build Complete!
echo ==================================================
echo.
echo Built images:
docker images | findstr "pulsai.*local"
echo.
echo Next steps:
echo.
echo 1. Start all services:
echo    docker-compose -f docker-compose.local-build.yaml up -d
echo.
echo 2. View logs:
echo    docker-compose -f docker-compose.local-build.yaml logs -f
echo.
echo 3. Access Pulsai:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8080
echo.
echo Happy coding! 🚀



