@echo off
REM Pulsai Docker Build Script for Windows
REM Builds all Pulsai Docker images

setlocal enabledelayedexpansion

REM Default values
set USE_CUDA=false
set USE_SLIM=false
set NO_CACHE=
set PUSH=false
set TAG=latest

REM Parse arguments
:parse_args
if "%~1"=="" goto :end_parse
if /i "%~1"=="--cuda" (
    set USE_CUDA=true
    shift
    goto :parse_args
)
if /i "%~1"=="--gpu" (
    set USE_CUDA=true
    shift
    goto :parse_args
)
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
if /i "%~1"=="--push" (
    set PUSH=true
    shift
    goto :parse_args
)
if /i "%~1"=="--tag" (
    set TAG=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-h" goto :help
if /i "%~1"=="--help" goto :help

echo Unknown option: %~1
exit /b 1

:help
echo Pulsai Docker Build Script for Windows
echo.
echo Usage: build-pulsai.bat [options]
echo.
echo Options:
echo   --cuda, --gpu    Build with CUDA/GPU support
echo   --slim           Build slim version (no models)
echo   --no-cache       Build without Docker cache
echo   --push           Push to registry after build
echo   --tag ^<tag^>      Custom tag (default: latest)
echo   -h, --help       Show this help message
exit /b 0

:end_parse

REM Print configuration
echo ===================================================
echo    Pulsai Docker Build Configuration
echo ===================================================
echo Tag:        %TAG%
echo CUDA:       %USE_CUDA%
echo Slim:       %USE_SLIM%
echo No Cache:   %NO_CACHE%
echo Push:       %PUSH%
echo ===================================================
echo.

REM Get build hash
for /f "delims=" %%i in ('git rev-parse --short HEAD 2^>nul') do set BUILD_HASH=%%i
if "%BUILD_HASH%"=="" set BUILD_HASH=dev-build

echo Build Hash: %BUILD_HASH%
echo.

REM Build Backend
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Building Pulsai Backend (pulsai/backend:%TAG%)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

docker build ^
    %NO_CACHE% ^
    --build-arg USE_CUDA=%USE_CUDA% ^
    --build-arg USE_SLIM=%USE_SLIM% ^
    --build-arg BUILD_HASH=%BUILD_HASH% ^
    -t pulsai/backend:%TAG% ^
    -f Dockerfile ^
    .

if errorlevel 1 (
    echo Backend build failed
    exit /b 1
)

echo Backend image built successfully
echo.

if not "%TAG%"=="latest" (
    docker tag pulsai/backend:%TAG% pulsai/backend:latest
    echo Tagged as pulsai/backend:latest
)

REM Build MCP Server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Building Pulsai MCP Server (pulsai/mcp:%TAG%)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if exist mcp-server (
    docker build ^
        %NO_CACHE% ^
        -t pulsai/mcp:%TAG% ^
        -f mcp-server\Dockerfile ^
        mcp-server\
    
    if errorlevel 1 (
        echo MCP server build failed
        exit /b 1
    )
    
    echo MCP server image built successfully
    
    if not "%TAG%"=="latest" (
        docker tag pulsai/mcp:%TAG% pulsai/mcp:latest
        echo Tagged as pulsai/mcp:latest
    )
) else (
    echo MCP server directory not found, skipping
)

echo.
echo ===================================================
echo    Build Complete
echo ===================================================
echo.
echo Built images:
docker images | findstr pulsai
echo.

REM Push if requested
if "%PUSH%"=="true" (
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo Pushing images to registry
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    docker push pulsai/backend:%TAG%
    docker push pulsai/mcp:%TAG%
    
    if not "%TAG%"=="latest" (
        docker push pulsai/backend:latest
        docker push pulsai/mcp:latest
    )
    
    echo Images pushed successfully
    echo.
)

REM Next steps
echo Next steps:
echo.
echo 1. Run Pulsai with Docker Compose:
echo    docker-compose -f docker-compose.pulsai.yaml up -d
echo.
echo 2. Or run backend standalone:
echo    docker run -d -p 8080:8080 -v pulsai-data:/app/backend/data pulsai/backend:%TAG%
echo.
echo 3. Check logs:
echo    docker-compose -f docker-compose.pulsai.yaml logs -f
echo.
echo 4. Access Pulsai:
echo    http://localhost:8080
echo.
echo Happy Pulsai-ing! 🚀

endlocal

