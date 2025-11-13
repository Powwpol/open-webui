@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ==================================================
echo    Lancement PulsAI Monolithe
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

:: Vérifier l'image
echo [1/3] Verification de l'image pulsai/monolith:latest...
docker images pulsai/monolith:latest --format "{{.Repository}}:{{.Tag}}" 2>nul | findstr "pulsai/monolith:latest" >nul
IF ERRORLEVEL 1 (
    echo [ERREUR] L'image pulsai/monolith:latest n'existe pas.
    echo.
    echo Veuillez construire l'image d'abord avec:
    echo   build-monolith.bat
    echo.
    pause
    exit /b 1
)
echo [OK] Image trouvee.
docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo.

:: Arrêter l'ancien conteneur s'il existe
echo [2/3] Nettoyage des anciens conteneurs...
docker-compose -f docker-compose.monolith.yaml down 2>nul
echo.

:: Démarrer
echo [3/3] Demarrage du monolithe...
docker-compose -f docker-compose.monolith.yaml up -d

IF ERRORLEVEL 1 (
    echo.
    echo [ERREUR] Le demarrage a echoue.
    echo.
    echo Affichage des logs...
    timeout /t 3 /nobreak >nul
    docker-compose -f docker-compose.monolith.yaml logs
    pause
    exit /b 1
)

echo.
echo [OK] Services demarres!
echo.
echo Attente du demarrage complet (30 secondes)...
timeout /t 30 /nobreak

echo.
echo ==================================================
echo    Status des Services
echo ==================================================
docker ps --filter "name=pulsai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

:: Vérifier le backend
docker ps --filter "name=pulsai-monolith" --filter "status=running" --format "{{.Names}}" 2>nul | findstr "pulsai-monolith" >nul
IF ERRORLEVEL 1 (
    echo [ATTENTION] Le conteneur monolithe ne semble pas demarrer correctement.
    echo.
    echo Derniers logs:
    echo ================================================
    docker logs pulsai-monolith --tail 100 2>&1
    echo ================================================
    echo.
) else (
    echo ==================================================
    echo     Pulsai Monolithe est PRET!
    echo ==================================================
    echo.
    echo Acces:
    echo   - Interface Web: http://localhost:3000
    echo   - Backend API: http://localhost:3000/api/docs
    echo.
    echo Services:
    echo   - Ollama: http://localhost:11434
    echo   - Redis: localhost:6379
    echo.
    echo Commandes utiles:
    echo   - Voir les logs: docker logs pulsai-monolith -f
    echo   - Arreter: docker-compose -f docker-compose.monolith.yaml down
    echo   - Redemarrer: docker-compose -f docker-compose.monolith.yaml restart
    echo.
)

pause

