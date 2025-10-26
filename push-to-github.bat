@echo off
REM Push automatique vers GitHub (après création du repo)

echo ==================================================
echo    📤 Push vers GitHub - Pulsai
echo ==================================================
echo.

echo Vérification du repo GitHub...
git remote -v

if errorlevel 1 (
    echo ❌ Aucun remote configuré!
    echo.
    echo Exécutez d'abord: init-github.bat
    pause
    exit /b 1
)

echo.
echo Création de la branche main...
git branch -M main

echo.
echo Push vers GitHub...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors du push!
    echo.
    echo Solutions:
    echo   1. Vérifiez que le repo existe sur GitHub
    echo   2. Utilisez un Personal Access Token comme mot de passe
    echo      https://github.com/settings/tokens
    echo.
    echo   3. Ou configurez SSH:
    echo      ssh-keygen -t ed25519 -C "your-email@example.com"
    echo      Puis ajoutez la clé publique sur GitHub
    pause
    exit /b 1
)

echo.
echo ==================================================
echo    ✅ Push Réussi!
echo ==================================================
echo.

REM Récupérer le remote URL
for /f "tokens=2" %%i in ('git remote get-url origin') do set REPO_URL=%%i

echo Votre repo Pulsai est maintenant sur GitHub:
echo   %REPO_URL:.git=%
echo.
echo Prochaines étapes:
echo   - Vérifier les fichiers sur GitHub
echo   - Créer un README.md Pulsai
echo   - Ajouter une description
echo   - Créer votre première release (v1.0.0)
echo.

pause

