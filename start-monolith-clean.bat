@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ==================================================
echo    Demarrage Propre PulsAI Monolithe
echo ==================================================
echo.

:: Vérifier Docker
docker info >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Docker n'est pas en cours d'execution.
    echo Veuillez demarrer Docker Desktop.
    pause
    exit /b 1
)

echo [1/4] Arret des services existants...
docker-compose -f docker-compose.github.yaml down 2>nul
docker-compose -f docker-compose.monolith.yaml down 2>nul
echo [OK] Services arretes.
echo.

echo [2/4] Verification de l'image pulsai/monolith:latest...
docker images pulsai/monolith:latest --format "{{.Repository}}:{{.Tag}}" 2>nul | findstr "pulsai/monolith:latest" >nul
IF ERRORLEVEL 1 (
    echo [ERREUR] L'image pulsai/monolith:latest n'existe pas.
    echo.
    echo Veuillez d'abord construire l'image avec:
    echo   build-monolith.bat
    echo.
    echo Ou attendre que le build en cours se termine.
    pause
    exit /b 1
) else (
    echo [OK] Image trouvee:
    docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
)
echo.

echo [3/4] Demarrage des services monolithe...
docker-compose -f docker-compose.monolith.yaml up -d
IF ERRORLEVEL 1 (
    echo [ERREUR] Le demarrage a echoue.
    pause
    exit /b 1
)
echo [OK] Services demarres.
echo.

echo [4/4] Verification du demarrage (30 secondes)...
timeout /t 30 /nobreak >nul
echo.

echo Status des conteneurs:
echo ================================================
docker ps --filter "name=pulsai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ================================================
echo.

:: Vérifier le backend
docker ps --filter "name=pulsai-monolith" --filter "status=running" --format "{{.Names}}" 2>nul | findstr "pulsai-monolith" >nul
IF ERRORLEVEL 1 (
    echo [ATTENTION] Le conteneur ne semble pas en cours d'execution.
    echo.
    echo Logs du conteneur:
    echo ================================================
    docker logs pulsai-monolith --tail 100 2>&1
    echo ================================================
    echo.
) else (
    echo [OK] PulsAI Monolithe demarre avec succes!
    echo.
    echo ==================================================
    echo     PulsAI est pret!
    echo ==================================================
    echo.
    echo Acces:
    echo   - Interface Web: http://localhost:3000
    echo   - Ollama: http://localhost:11434
    echo.
    echo Logs en temps reel:
    echo   docker logs pulsai-monolith -f
    echo.
    echo Arreter:
    echo   docker-compose -f docker-compose.monolith.yaml down
    echo.
)

pause

