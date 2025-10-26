@echo off
REM Quick Docker WSL2 Fix for Pulsai

echo ==================================================
echo    Pulsai Docker Quick Fix
echo ==================================================
echo.

echo Step 1: Stopping Docker Desktop...
taskkill /F /IM "Docker Desktop.exe" >nul 2>&1
timeout /t 3 >nul
echo Done
echo.

echo Step 2: Shutting down WSL...
wsl --shutdown
timeout /t 5 >nul
echo Done
echo.

echo Step 3: Cleaning Docker cache...
docker system prune -af --volumes >nul 2>&1
echo Done
echo.

echo Step 4: Restarting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
echo Waiting 30 seconds for Docker to start...
timeout /t 30 >nul
echo.

echo Step 5: Verifying Docker...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker is running!
) else (
    echo Docker not responding yet, wait a bit more...
)
echo.

echo ==================================================
echo    Fix Complete
echo ==================================================
echo.
echo Try building again with slim version (faster):
echo    build-pulsai.bat --slim
echo.
echo Or force clean build:
echo    build-pulsai.bat --no-cache --slim
echo.

pause

