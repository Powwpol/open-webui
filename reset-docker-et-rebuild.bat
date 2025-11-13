@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ==================================================
echo    Reset Docker et Rebuild PulsAI Monolith
echo ==================================================
echo.

echo [ATTENTION] Cette operation va:
echo   1. Arreter tous les builds en cours
echo   2. Redemarrer Docker Desktop
echo   3. Nettoyer le cache Docker
echo   4. Lancer UN SEUL build propre
echo.
echo Les donnees de vos conteneurs seront preservees.
echo.
set /p CONFIRM=Continuer? (O/N): 
if /i not "%CONFIRM%"=="O" (
    echo Operation annulee.
    pause
    exit /b 0
)

echo.
echo ==================================================
echo    Etape 1/5: Arret des builds
echo ==================================================
echo.

echo Arret des builds Docker...
docker buildx stop >nul 2>&1
taskkill /F /IM docker-buildx.exe >nul 2>&1
echo [OK] Builds arretes.
timeout /t 2 /nobreak >nul

echo.
echo ==================================================
echo    Etape 2/5: Arret des conteneurs
echo ==================================================
echo.

docker-compose -f docker-compose.monolith.yaml down >nul 2>&1
docker-compose -f docker-compose.github.yaml down >nul 2>&1
echo [OK] Conteneurs arretes.

echo.
echo ==================================================
echo    Etape 3/5: Redemarrage de Docker Desktop
echo ==================================================
echo.

echo Arret de Docker Desktop...
taskkill /IM "Docker Desktop.exe" /F >nul 2>&1
timeout /t 5 /nobreak >nul

echo Demarrage de Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo Attente du demarrage de Docker (30 secondes)...
timeout /t 30 /nobreak

:CHECK_DOCKER
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker n'est pas encore pret, attente de 10 secondes...
    timeout /t 10 /nobreak
    goto :CHECK_DOCKER
)

echo [OK] Docker est pret.

echo.
echo ==================================================
echo    Etape 4/5: Nettoyage du cache Docker
echo ==================================================
echo.

echo Nettoyage du builder cache...
docker builder prune -a -f
echo [OK] Cache nettoye.

echo.
echo ==================================================
echo    Etape 5/5: Build de l'image PulsAI Monolith
echo ==================================================
echo.

echo Construction de l'image (15-25 minutes)...
echo.
echo Configuration:
echo   - Image: pulsai/monolith:latest
echo   - USE_CUDA: false
echo   - USE_SLIM: false
echo   - Taille finale: ~8.6 GB
echo.

docker build ^
  --progress=plain ^
  --build-arg USE_CUDA=false ^
  --build-arg USE_SLIM=false ^
  -t pulsai/monolith:latest ^
  -f Dockerfile ^
  .

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================================
    echo     BUILD REUSSI !
    echo ==================================================
    echo.
    docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo.
    echo Prochaine etape: Lancer le conteneur
    echo   start-monolith-clean.bat
    echo.
) else (
    echo.
    echo ==================================================
    echo     BUILD ECHOUE
    echo ==================================================
    echo.
    echo Consultez les logs ci-dessus pour plus de details.
    echo.
)

pause

