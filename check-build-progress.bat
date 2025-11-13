@echo off
cls
echo ==================================================
echo    Verification Build PulsAI Monolith
echo ==================================================
echo.

echo [1] Processus de build en cours:
echo ================================================
powershell -Command "Get-Process docker-buildx -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count" > temp_count.txt
set /p BUILD_COUNT=<temp_count.txt
del temp_count.txt

if "%BUILD_COUNT%"=="0" (
    echo   Aucun build en cours
) else (
    echo   %BUILD_COUNT% build^(s^) en cours
    echo.
    echo   Processus Docker actifs:
    powershell -Command "Get-Process | Where-Object {$_.ProcessName -like '*docker*'} | Select-Object ProcessName, @{Name='CPU(s)';Expression={[math]::Round($_.CPU,1)}}, @{Name='Memory(MB)';Expression={[math]::Round($_.WorkingSet/1MB,1)}} | Sort-Object 'CPU(s)' -Descending | Format-Table -AutoSize"
)
echo ================================================
echo.

echo [2] État de l'image:
echo ================================================
docker images pulsai/monolith:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ================================================
echo.

echo [3] Utilisation de l'espace Docker:
echo ================================================
docker system df
echo ================================================
echo.

echo [4] Conteneurs PulsAI:
echo ================================================
docker ps -a --filter "name=pulsai" --format "table {{.Names}}\t{{.Status}}" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   Aucun conteneur PulsAI
)
echo ================================================
echo.

if not "%BUILD_COUNT%"=="0" (
    echo INFO: Build en cours, veuillez patienter...
    echo       Temps estime: 15-25 minutes
    echo.
    echo       Relancez ce script regulierement pour suivre la progression.
) else (
    echo INFO: Aucun build en cours.
    echo.
    echo       Si l'image a ete mise a jour recemment ^(voir "CREATED" ci-dessus^),
    echo       le build est termine et vous pouvez lancer:
    echo         start-monolith-clean.bat
    echo.
    echo       Sinon, relancez le build avec:
    echo         build-monolith-fix.bat
)
echo.

pause
