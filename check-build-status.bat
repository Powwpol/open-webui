@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ==================================================
echo    Verification du Build PulsAI
echo ==================================================
echo.

:: Vérifier Docker
docker info >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Docker n'est pas en cours d'execution.
    pause
    exit /b 1
)

echo [1] Images PulsAI actuelles:
echo ================================================
docker images | findstr pulsai
IF ERRORLEVEL 1 (
    echo Aucune image pulsai trouvee.
)
echo.

echo [2] Conteneurs PulsAI (tous):
echo ================================================
docker ps -a | findstr pulsai
IF ERRORLEVEL 1 (
    echo Aucun conteneur pulsai trouve.
)
echo.

echo [3] Conteneurs PulsAI en cours d'execution:
echo ================================================
docker ps | findstr pulsai
IF ERRORLEVEL 1 (
    echo Aucun conteneur pulsai en cours d'execution.
)
echo.

echo [4] Verification de l'image monolithe:
echo ================================================
docker images pulsai/monolith:latest --format "{{.Repository}}:{{.Tag}}" 2>nul | findstr "pulsai/monolith:latest" >nul
IF ERRORLEVEL 1 (
    echo [INFO] Image pulsai/monolith:latest n'existe pas encore.
    echo       Le build est peut-etre en cours...
    echo.
    echo Pour verifier si un build est en cours:
    echo   docker ps ^| findstr build
) else (
    echo [OK] Image pulsai/monolith:latest existe!
    docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo.
    echo L'image est prete! Vous pouvez lancer:
    echo   start-monolith-simple.bat
)
echo.

echo [5] Processes Docker Build en cours:
echo ================================================
docker ps -a --filter "ancestor=docker" 2>nul
echo.

echo ==================================================
echo    Informations Systeme Docker
echo ==================================================
echo.
echo Espace disque:
docker system df
echo.

pause

