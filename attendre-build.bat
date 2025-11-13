@echo off
cls
echo ==================================================
echo    Attente de la fin du Build PulsAI
echo ==================================================
echo.

echo Build en cours...
echo.

:LOOP
timeout /t 10 /nobreak >nul

REM Vérifier si le build est encore actif
powershell -Command "Get-Process docker-buildx -ErrorAction SilentlyContinue" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Build encore en cours... Verification dans 10 secondes
    goto :LOOP
)

echo.
echo ==================================================
echo    Build Termine !
echo ==================================================
echo.

echo Verification de l'image:
docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo.
echo Voulez-vous demarrer PulsAI maintenant? (O/N)
set /p START=Reponse: 
if /i "%START%"=="O" (
    call start-monolith-clean.bat
) else (
    echo.
    echo Pour demarrer plus tard, utilisez:
    echo   start-monolith-clean.bat
    echo.
    pause
)


