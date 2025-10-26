@echo off
REM Build Pulsai en UN SEUL conteneur (Frontend + Backend)

echo ==================================================
echo    Pulsai Monolith Build (All-in-One)
echo ==================================================
echo.

REM Parse arguments
set SLIM=false
set NO_CACHE=
set TAG=latest

:parse
if "%~1"=="" goto :build
if /i "%~1"=="--slim" set SLIM=true
if /i "%~1"=="--no-cache" set NO_CACHE=--no-cache
if /i "%~1"=="--tag" set TAG=%~2& shift
shift
goto :parse

:build
echo Configuration:
echo   Slim: %SLIM%
echo   No Cache: %NO_CACHE%
echo   Tag: %TAG%
echo.

echo Building Pulsai Monolith (Frontend + Backend in ONE container)...
echo ============================================================

docker build %NO_CACHE% ^
  --build-arg USE_CUDA=false ^
  --build-arg USE_SLIM=%SLIM% ^
  -t pulsai/monolith:%TAG% ^
  -f Dockerfile ^
  .

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================================
    echo    ✅ Monolith Build Complete!
    echo ==================================================
    echo.
    echo Built image:
    echo   pulsai/monolith:%TAG%
    echo.
    echo To run:
    echo   docker run -d -p 3000:8080 -v pulsai-data:/app/backend/data pulsai/monolith:%TAG%
    echo.
    echo Access:
    echo   Frontend + Backend: http://localhost:3000
    echo.
) else (
    echo.
    echo ❌ Monolith build failed!
    exit /b 1
)



