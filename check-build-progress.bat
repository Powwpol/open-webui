@echo off
REM Script pour vérifier la progression du build Pulsai

echo ==================================================
echo    Vérification Build Pulsai
echo ==================================================
echo.

echo Checking Docker images...
docker images | findstr "pulsai"
echo.

echo Checking running builds (containers)...
docker ps -a | findstr "build"
echo.

echo Checking logs of recent builds...
echo.
echo To see live logs of specific build:
echo   docker logs -f ^<container-id^>
echo.
echo To see all Docker processes:
echo   docker ps -a
echo.

pause



