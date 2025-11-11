@echo off
REM ========================================
REM Script Complet : Upload Pulsai vers GitHub
REM ========================================

echo.
echo ================================================
echo    🚀 Upload Complet Pulsai vers GitHub
echo ================================================
echo.

REM Variables
set GITHUB_USER=
set TOKEN=

REM Demander le username
set /p GITHUB_USER="Entrez votre username GitHub: "

if "%GITHUB_USER%"=="" (
    echo.
    echo ❌ Erreur: Username requis!
    pause
    exit /b 1
)

echo.
echo ================================================
echo    Configuration
echo ================================================
echo.
echo   Username: %GITHUB_USER%
echo   Repo:     pulsai
echo   URL:      https://github.com/%GITHUB_USER%/pulsai
echo.

REM Vérifier Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git n'est pas installé!
    echo.
    echo Téléchargez: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git installé
echo.

REM ================================================
REM Étape 1: Vérifier le commit
REM ================================================

echo ================================================
echo    Étape 1/4: Vérification
echo ================================================
echo.

git log -1 --oneline >nul 2>&1
if errorlevel 1 (
    echo ❌ Aucun commit trouvé!
    echo.
    echo Créez un commit d'abord:
    echo   git add .
    echo   git commit -m "Initial commit"
    pause
    exit /b 1
)

echo ✅ Commit prêt:
git log -1 --oneline
echo.

REM ================================================
REM Étape 2: Nettoyer et configurer remote
REM ================================================

echo ================================================
echo    Étape 2/4: Configuration Remote
echo ================================================
echo.

REM Supprimer remote existant
git remote remove origin >nul 2>&1

REM Ajouter nouveau remote
git remote add origin https://github.com/%GITHUB_USER%/pulsai.git

echo ✅ Remote configuré: https://github.com/%GITHUB_USER%/pulsai.git
echo.

REM ================================================
REM Étape 3: Renommer branche
REM ================================================

echo ================================================
echo    Étape 3/4: Branche → main
echo ================================================
echo.

git branch -M main
echo ✅ Branche renommée en 'main'
echo.

REM ================================================
REM Étape 4: Push vers GitHub
REM ================================================

echo ================================================
echo    Étape 4/4: Upload vers GitHub
echo ================================================
echo.
echo ⏳ Upload de 613 fichiers en cours...
echo    (Cela peut prendre 2-5 minutes)
echo.
echo 🔑 AUTHENTIFICATION:
echo    - Username: %GITHUB_USER%
echo    - Password: Utilisez votre PERSONAL ACCESS TOKEN
echo                (PAS votre mot de passe GitHub!)
echo.
echo    Token format: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
echo.
echo 📖 Créer un token: https://github.com/settings/tokens
echo    → Generate new token (classic)
echo    → Cocher 'repo'
echo    → Generate token
echo    → Copier le token
echo.

pause

git push -u origin main

if errorlevel 1 (
    echo.
    echo ================================================
    echo    ❌ Erreur lors du push
    echo ================================================
    echo.
    echo Causes possibles:
    echo   1. Repo 'pulsai' n'existe pas sur GitHub
    echo      → Créez-le sur https://github.com/new
    echo.
    echo   2. Mauvais token ou username
    echo      → Vérifiez votre username: %GITHUB_USER%
    echo      → Utilisez un Personal Access Token (pas mot de passe)
    echo.
    echo   3. Token sans permission 'repo'
    echo      → Créez nouveau token avec scope 'repo'
    echo.
    echo   4. Le repo existe déjà avec du contenu
    echo      → Utilisez: git push -u origin main --force
    echo.
    pause
    exit /b 1
)

REM ================================================
REM Succès !
REM ================================================

echo.
echo ================================================
echo    ✅ UPLOAD RÉUSSI !
echo ================================================
echo.
echo 🎉 Pulsai est maintenant sur GitHub!
echo.
echo 📍 Votre repo:
echo    https://github.com/%GITHUB_USER%/pulsai
echo.
echo 📊 Uploadé:
echo    - 613 fichiers
echo    - ~56,000 lignes de code
echo    - Backend rebrandé (Pulsai)
echo    - Frontend + 58 langues
echo    - MCP server custom
echo    - Docker configs
echo    - Documentation complète
echo.
echo 🔗 Prochaines étapes:
echo.
echo 1. Vérifier sur GitHub:
echo    https://github.com/%GITHUB_USER%/pulsai
echo.
echo 2. Partager avec votre équipe:
echo    git clone https://github.com/%GITHUB_USER%/pulsai.git
echo.
echo 3. Configurer description/topics:
echo    → Sur GitHub → About → ⚙️
echo.
echo ================================================
echo.

pause

