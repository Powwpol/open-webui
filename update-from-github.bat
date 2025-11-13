@echo off
REM ========================================
REM Update Pulsai depuis GitHub
REM Pull + Rebuild + Restart
REM ========================================

echo.
echo ==================================================
echo    🔄 Update Pulsai depuis GitHub
echo ==================================================
echo.

set GITHUB_REPO=https://github.com/Powwpol/open-webui.git
set BRANCH=main
set COMPOSE_FILE=docker-compose.github.yaml

echo Configuration:
echo   - Source: %GITHUB_REPO%
echo   - Branch: %BRANCH%
echo.

REM ========================================
REM Étape 1: Pull latest code
REM ========================================

echo ================================================
echo    Étape 1/4: Pull Latest Code
echo ================================================
echo.

if exist .git (
    echo 📥 Pulling latest changes from GitHub...
    git fetch origin
    git pull origin %BRANCH%
    
    if errorlevel 1 (
        echo.
        echo ⚠️ Pull failed, reset to remote
        git reset --hard origin/%BRANCH%
    )
    
    echo ✅ Code updated
) else (
    echo ⚠️ Not a git repository
    echo Clone first with: git clone %GITHUB_REPO%
    pause
    exit /b 1
)
echo.

REM ========================================
REM Étape 2: Stop services
REM ========================================

echo ================================================
echo    Étape 2/4: Stop Services
echo ================================================
echo.

docker-compose -f %COMPOSE_FILE% down
echo ✅ Services stopped
echo.

REM ========================================
REM Étape 3: Rebuild images
REM ========================================

echo ================================================
echo    Étape 3/4: Rebuild Images
echo ================================================
echo.
echo ⏳ Building...
echo.

docker-compose -f %COMPOSE_FILE% build

if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo ✅ Images rebuilt
echo.

REM ========================================
REM Étape 4: Restart services
REM ========================================

echo ================================================
echo    Étape 4/4: Restart Services
echo ================================================
echo.

docker-compose -f %COMPOSE_FILE% up -d

if errorlevel 1 (
    echo.
    echo ❌ Start failed!
    pause
    exit /b 1
)

echo ✅ Services restarted
echo.

timeout /t 5 >nul

REM ========================================
REM Summary
REM ========================================

echo ================================================
echo    ✅ Update Complet!
echo ================================================
echo.

echo Services:
docker-compose -f %COMPOSE_FILE% ps
echo.

echo Latest commit:
git log -1 --oneline
echo.

echo 🌐 Access:
echo    http://localhost:8080
echo.
echo 📊 Logs:
echo    docker-compose -f %COMPOSE_FILE% logs -f
echo.

pause

