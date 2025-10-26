@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Script de lancement pour Open WebUI avec Docker (Windows)
echo ===================================================
echo     Open WebUI - Lancement avec Docker
echo ===================================================
echo.

:: Vérifier si Docker est installé
docker --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Docker n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: Vérifier si Docker est en cours d'exécution
docker info >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Docker n'est pas en cours d'execution.
    echo Veuillez demarrer Docker Desktop.
    pause
    exit /b 1
)

:: Créer le dossier de données si nécessaire
IF NOT EXIST "backend\data" (
    mkdir backend\data
)

:: Traiter les arguments
IF "%1"=="" GOTO :DEFAULT
IF /I "%1"=="build" GOTO :BUILD
IF /I "%1"=="start" GOTO :START
IF /I "%1"=="stop" GOTO :STOP
IF /I "%1"=="restart" GOTO :RESTART
IF /I "%1"=="logs" GOTO :LOGS
IF /I "%1"=="clean" GOTO :CLEAN
IF /I "%1"=="help" GOTO :HELP
GOTO :DEFAULT

:BUILD
echo [INFO] Construction de l'image Docker...
docker compose -f docker-compose.local.yaml build
IF ERRORLEVEL 1 (
    echo [ERREUR] La construction a echoue.
    pause
    exit /b 1
)
echo [OK] Construction terminee avec succes!
GOTO :END

:START
echo [INFO] Demarrage des services...
docker compose -f docker-compose.local.yaml up -d
IF ERRORLEVEL 1 (
    echo [ERREUR] Le demarrage a echoue.
    pause
    exit /b 1
)
echo.
echo [OK] Open WebUI est accessible sur http://localhost:3000
GOTO :END

:STOP
echo [INFO] Arret des services...
docker compose -f docker-compose.local.yaml down
echo [OK] Services arretes.
GOTO :END

:RESTART
echo [INFO] Redemarrage des services...
docker compose -f docker-compose.local.yaml restart
echo [OK] Services redemarres.
GOTO :END

:LOGS
echo [INFO] Affichage des logs (Ctrl+C pour quitter)...
docker compose -f docker-compose.local.yaml logs -f
GOTO :END

:CLEAN
echo [INFO] Nettoyage des conteneurs et images...
docker compose -f docker-compose.local.yaml down -v
docker rmi open-webui-local 2>nul
echo [OK] Nettoyage termine.
GOTO :END

:HELP
echo Usage: start-docker.bat [OPTION]
echo.
echo Options disponibles:
echo   build    - Construire l'image Docker
echo   start    - Demarrer les services
echo   stop     - Arreter les services
echo   restart  - Redemarrer les services
echo   logs     - Afficher les logs
echo   clean    - Nettoyer les conteneurs et images
echo   help     - Afficher cette aide
echo.
echo Par defaut (sans option), le script va construire et demarrer les services.
GOTO :END

:DEFAULT
:: Par défaut, construire et démarrer
echo [INFO] Construction de l'image Docker...
docker compose -f docker-compose.local.yaml build
IF ERRORLEVEL 1 (
    echo [ERREUR] La construction a echoue.
    pause
    exit /b 1
)

echo.
echo [INFO] Demarrage des services...
docker compose -f docker-compose.local.yaml up -d
IF ERRORLEVEL 1 (
    echo [ERREUR] Le demarrage a echoue.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo     Open WebUI demarre avec succes!
echo ===================================================
echo.
echo [OK] Interface accessible sur: http://localhost:3000
echo.
echo Commandes utiles:
echo   - Pour voir les logs: start-docker.bat logs
echo   - Pour arreter: start-docker.bat stop
echo   - Pour redemarrer: start-docker.bat restart
echo.

:END
pause

