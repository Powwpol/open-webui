@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

cls
echo ==================================================
echo    Build et Demarrage PulsAI depuis GitHub
echo ==================================================
echo.

echo Configuration:
echo   - Source: GitHub (contexte local avec modifications)
echo   - Image: pulsai/backend:github
echo   - Correctif: pulsai.main:app (✓ applique)
echo   - Services: Backend + Redis + Ollama + MCP
echo.

echo [INFO] Build en cours en arriere-plan...
echo        Temps estime: 10-15 minutes
echo.

:CHECK_BUILD
timeout /t 15 /nobreak >nul

REM Vérifier si le build est encore actif
powershell -Command "Get-Process docker-buildx -ErrorAction SilentlyContinue" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Build en cours... (verification dans 15s)
    goto :CHECK_BUILD
)

echo.
echo ==================================================
echo    Build Termine !
echo ==================================================
echo.

echo Verification de l'image:
docker images pulsai/backend:github --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo.
echo [INFO] Demarrage de tous les services...
echo.

docker-compose -f docker-compose.github.yaml up -d

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================================
    echo     PULSAI DEMARRE !
    echo ==================================================
    echo.
    echo Attente du demarrage complet (30 secondes)...
    timeout /t 30 /nobreak >nul
    
    echo.
    echo Status des services:
    echo ================================================
    docker ps --filter "name=pulsai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ================================================
    echo.
    
    echo Logs du backend:
    echo ================================================
    docker logs pulsai-backend-github --tail 30
    echo ================================================
    echo.
    
    docker ps --filter "name=pulsai-backend-github" --filter "status=running" --format "{{.Names}}" 2>nul | findstr "pulsai-backend-github" >nul
    IF NOT ERRORLEVEL 1 (
        echo.
        echo ✓ PulsAI est accessible sur: http://localhost:8080
        echo ✓ Documentation API: http://localhost:8080/api/docs
        echo ✓ Ollama: http://localhost:11434
        echo.
    ) else (
        echo.
        echo [ATTENTION] Le backend ne semble pas demarrer correctement.
        echo Consultez les logs ci-dessus.
        echo.
    )
) else (
    echo.
    echo [ERREUR] Le demarrage a echoue.
    echo.
)

pause

