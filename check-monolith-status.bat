@echo off
echo ==================================================
echo    Status PulsAI Monolith
echo ==================================================
echo.

echo [1] Image Docker:
echo ================================================
docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ================================================
echo.

echo [2] Conteneurs en cours:
echo ================================================
docker ps --filter "name=pulsai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ================================================
echo.

echo [3] Tous les conteneurs PulsAI:
echo ================================================
docker ps -a --filter "name=pulsai" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
echo ================================================
echo.

echo [4] Test de connexion:
echo ================================================
echo Backend (port 3000):
curl -s http://localhost:3000/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend accessible
) else (
    echo [ERREUR] Backend non accessible
)
echo.
echo Ollama (port 11434):
curl -s http://localhost:11434/api/tags 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Ollama accessible
) else (
    echo [ERREUR] Ollama non accessible
)
echo ================================================
echo.

pause

