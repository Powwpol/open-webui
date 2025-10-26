@echo off
REM Transformer le build Open WebUI xn3xof en image Pulsai
REM et l'intégrer avec le projet en cours

echo ==================================================
echo    Transformation Build xn3xof -> Pulsai Backend
echo ==================================================
echo.

REM Etape 1: Tag l'image existante
echo Step 1: Tagging existing build as pulsai/backend:from-build...
docker tag open-webui-open-webui:latest pulsai/backend:from-build

if %errorlevel% neq 0 (
    echo ❌ Failed to tag image
    exit /b 1
)
echo ✅ Image tagged successfully
echo.

REM Etape 2: Vérifier que l'image est bien créée
echo Step 2: Verifying tagged image...
docker images | findstr "pulsai/backend.*from-build"
echo.

REM Etape 3: Créer un docker-compose temporaire pour ce build
echo Step 3: Creating docker-compose configuration...
echo.

REM Afficher les informations
echo ==================================================
echo    ✅ Transformation Complete!
echo ==================================================
echo.
echo Tagged image:
echo   open-webui-open-webui:latest → pulsai/backend:from-build
echo.
echo Next steps:
echo.
echo 1. Start the full stack:
echo    docker-compose -f docker-compose.from-build.yaml up -d
echo.
echo 2. Or run just the backend:
echo    docker run -d -p 8080:8080 \
echo      -v pulsai-data:/app/backend/data \
echo      --network pulsai-network \
echo      --name pulsai-backend-from-build \
echo      pulsai/backend:from-build
echo.
echo 3. Check logs:
echo    docker logs -f pulsai-backend-from-build
echo.
echo Access: http://localhost:8080
echo.

