@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ==================================================
echo    Fix et Restart PulsAI - GitHub Build
echo ==================================================
echo.

:: Vérifier Docker
docker info >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Docker n'est pas en cours d'execution.
    pause
    exit /b 1
)

echo [1/5] Arret et nettoyage des anciens conteneurs...
docker-compose -f docker-compose.github.yaml down 2>nul
docker-compose -f docker-compose.monolith.yaml down 2>nul

:: Nettoyer les conteneurs orphelins
docker ps -a --filter "status=exited" --format "{{.ID}} {{.Image}}" | findstr "pulsai" >nul
IF NOT ERRORLEVEL 1 (
    echo [INFO] Nettoyage des conteneurs exited...
    for /f "tokens=1,2" %%i in ('docker ps -a --filter "status=exited" --format "{{.ID}} {{.Image}}"') do (
        echo %%j | findstr "pulsai" >nul
        if not errorlevel 1 (
            echo   Suppression du conteneur %%i ^(%%j^)
            docker rm %%i >nul 2>&1
        )
    )
)
echo.

echo [2/5] Verification de l'image pulsai/backend:github...
docker images pulsai/backend:github --format "{{.Repository}}:{{.Tag}}" 2>nul | findstr "pulsai/backend:github" >nul
IF ERRORLEVEL 1 (
    echo [INFO] Image non trouvee, elle sera construite.
    set NEED_BUILD=1
) else (
    echo [INFO] Image existante trouvee.
    echo.
    echo Voulez-vous reconstruire l'image? (O/N)
    echo (Necessaire si vous avez modifie le code)
    set /p REBUILD=Reponse: 
    if /i "!REBUILD!"=="O" (
        set NEED_BUILD=1
    ) else (
        set NEED_BUILD=0
    )
)
echo.

if "!NEED_BUILD!"=="1" (
    echo [3/5] Reconstruction de l'image (peut prendre 10-15 minutes)...
    echo Construction en cours...
    docker-compose -f docker-compose.github.yaml build --no-cache pulsai-backend
    IF ERRORLEVEL 1 (
        echo [ERREUR] La construction a echoue.
        echo.
        echo Solutions:
        echo   1. Verifiez les logs ci-dessus
        echo   2. Verifiez l'espace disque: docker system df
        echo   3. Essayez: docker system prune -f
        pause
        exit /b 1
    )
    echo [OK] Image construite avec succes!
) else (
    echo [3/5] Utilisation de l'image existante.
)
echo.

echo [4/5] Demarrage des services...
docker-compose -f docker-compose.github.yaml up -d
IF ERRORLEVEL 1 (
    echo [ERREUR] Le demarrage a echoue.
    echo.
    echo Affichage des logs...
    timeout /t 3 /nobreak >nul
    docker-compose -f docker-compose.github.yaml logs --tail 100
    pause
    exit /b 1
)
echo.

echo [5/5] Verification du demarrage...
echo Attente de 10 secondes...
timeout /t 10 /nobreak >nul

echo.
echo Status des conteneurs:
echo ================================================
docker ps --filter "name=pulsai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ================================================
echo.

:: Vérifier si le backend a démarré correctement
docker ps --filter "name=pulsai-backend-github" --filter "status=running" --format "{{.Names}}" 2>nul | findstr "pulsai-backend-github" >nul
IF ERRORLEVEL 1 (
    echo [ATTENTION] Le conteneur backend ne semble pas en cours d'execution.
    echo.
    echo Logs du backend:
    echo ================================================
    docker logs pulsai-backend-github --tail 50 2>&1
    echo ================================================
    echo.
    echo Que souhaitez-vous faire?
    echo   1. Voir les logs en temps reel
    echo   2. Redemarrer le backend
    echo   3. Quitter
    set /p ACTION=Votre choix (1-3): 
    
    if "!ACTION!"=="1" (
        docker logs pulsai-backend-github -f
    )
    if "!ACTION!"=="2" (
        docker-compose -f docker-compose.github.yaml restart pulsai-backend
        timeout /t 5 /nobreak >nul
        docker logs pulsai-backend-github --tail 50
    )
) else (
    echo [OK] Backend demarre avec succes!
    echo.
    echo ==================================================
    echo     Pulsai est pret!
    echo ==================================================
    echo.
    echo Acces:
    echo   - Interface Web: http://localhost:8080
    echo   - API Docs: http://localhost:8080/api/docs
    echo   - Ollama: http://localhost:11434
    echo.
    echo Logs en temps reel:
    echo   docker-compose -f docker-compose.github.yaml logs -f
    echo.
    echo Arreter:
    echo   docker-compose -f docker-compose.github.yaml down
    echo.
)

pause

