@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ==================================================
echo    Build PulsAI Monolith (avec fix pulsai)
echo ==================================================
echo.

:: Vérifier Docker
docker info >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Docker n'est pas en cours d'execution.
    pause
    exit /b 1
)

echo [INFO] Arret de tous les builds en cours...
docker buildx stop >nul 2>&1
timeout /t 2 /nobreak >nul

echo [INFO] Nettoyage des anciens conteneurs...
docker-compose -f docker-compose.monolith.yaml down >nul 2>&1

echo.
echo ==================================================
echo    Demarrage du Build
echo ==================================================
echo.
echo Configuration:
echo   - Image: pulsai/monolith:latest
echo   - USE_CUDA: false
echo   - USE_SLIM: false (full avec modeles ML)
echo   - Build time: 15-25 minutes
echo   - Size: ~8.6 GB
echo.
echo Le build va commencer dans 3 secondes...
echo (Appuyez sur Ctrl+C pour annuler)
timeout /t 3 /nobreak
echo.

echo [BUILD] Construction en cours...
echo ================================================
echo.
echo Progression:
echo   [1/10] Telechargement base images
echo   [2/10] Installation systeme
echo   [3/10] npm install (Frontend)
echo   [4/10] npm build (Frontend) - 5-8 min
echo   [5/10] pip install (Backend)
echo   [6/10] Telechargement modeles ML
echo   [7/10] Assembly final
echo.
echo Temps estime total: 15-25 minutes
echo.
echo ================================================

docker build ^
  --progress=plain ^
  --build-arg USE_CUDA=false ^
  --build-arg USE_SLIM=false ^
  -t pulsai/monolith:latest ^
  -f Dockerfile ^
  .

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================================
    echo     BUILD REUSSI !
    echo ==================================================
    echo.
    echo Image construite:
    docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo.
    echo Prochaine etape:
    echo   start-monolith-clean.bat
    echo.
    echo Ou manuellement:
    echo   docker-compose -f docker-compose.monolith.yaml up -d
    echo.
) else (
    echo.
    echo ==================================================
    echo     BUILD ECHOUE !
    echo ==================================================
    echo.
    echo Solutions:
    echo   1. Verifiez l'espace disque: docker system df
    echo   2. Nettoyez: docker system prune -f
    echo   3. Relancez ce script
    echo.
    exit /b 1
)

pause

