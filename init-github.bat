@echo off
REM Script d'initialisation GitHub pour Pulsai
REM Usage: init-github.bat [votre-username-github]

echo ==================================================
echo    🚀 Initialisation GitHub - Pulsai
echo ==================================================
echo.

REM Récupérer le username GitHub
set GITHUB_USER=%1
if "%GITHUB_USER%"=="" (
    set /p GITHUB_USER="Entrez votre username GitHub: "
)

echo Configuration:
echo   - Username GitHub: %GITHUB_USER%
echo   - Repo name: pulsai
echo.

REM Vérifier si Git est installé
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git n'est pas installé!
    echo.
    echo Téléchargez Git depuis: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git installé
echo.

REM Étape 1: Vérifier l'état Git
echo Étape 1: Vérification du dépôt local...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

git status >nul 2>&1
if errorlevel 1 (
    echo 📦 Initialisation du dépôt Git...
    git init
    echo ✅ Dépôt Git initialisé
) else (
    echo ✅ Dépôt Git déjà initialisé
)
echo.

REM Étape 2: Nettoyer les anciens remotes
echo Étape 2: Nettoyage des remotes existants...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

git remote remove origin >nul 2>&1
git remote remove upstream >nul 2>&1
echo ✅ Remotes nettoyés
echo.

REM Étape 3: Configurer le nouveau remote
echo Étape 3: Configuration du remote GitHub...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set REPO_URL=https://github.com/%GITHUB_USER%/pulsai.git
echo Ajout remote: %REPO_URL%
git remote add origin %REPO_URL%
echo ✅ Remote ajouté
echo.

REM Étape 4: Vérifier .gitignore
echo Étape 4: Vérification .gitignore...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if exist .gitignore (
    echo ✅ .gitignore existe
    findstr /C:".env" .gitignore >nul
    if errorlevel 1 (
        echo ⚠️  Attention: .env pas dans .gitignore
    ) else (
        echo ✅ .env ignoré
    )
) else (
    echo ⚠️  .gitignore manquant
)
echo.

REM Étape 5: Ajouter tous les fichiers
echo Étape 5: Ajout des fichiers...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

git add .
echo ✅ Fichiers ajoutés au staging
echo.

REM Afficher le statut
echo Fichiers à commiter:
git status --short | findstr /V "^??"
echo.

REM Étape 6: Créer le commit initial
echo Étape 6: Création du commit initial...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

git commit -m "🎉 Initial commit: Pulsai rebrandé (fork Open WebUI)" -m "" -m "- Rebranding complet Open WebUI → Pulsai" -m "- 102 fichiers modifiés, ~822 occurrences remplacées" -m "- Configuration MCP complète (HTTPS, npx, Docker, WebSocket, SSE)" -m "- Support 4 utilisateurs en local" -m "- Charte graphique Pulsai appliquée" -m "- Interface en français" -m "" -m "Basé sur Open WebUI v0.6.32" -m "Conforme licence Open WebUI (clause 5.i: <50 utilisateurs)"

if errorlevel 1 (
    echo ❌ Erreur lors du commit
    pause
    exit /b 1
)

echo ✅ Commit créé
echo.

REM Étape 7: Instructions pour pousser
echo ==================================================
echo    ✅ Repo Git Préparé!
echo ==================================================
echo.
echo 📋 PROCHAINES ÉTAPES:
echo.
echo 1. Créer le repo sur GitHub:
echo    https://github.com/new
echo.
echo    Repository name: pulsai
echo    Visibility: Private (recommandé)
echo    ❌ Ne PAS initialiser avec README/License/.gitignore
echo.
echo 2. Une fois créé sur GitHub, exécuter:
echo.
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Si demande d'authentification:
echo    - Username: %GITHUB_USER%
echo    - Password: Utilisez un Personal Access Token
echo      (Créer sur: https://github.com/settings/tokens)
echo.
echo 4. Vérifier sur:
echo    https://github.com/%GITHUB_USER%/pulsai
echo.
echo ==================================================
echo.

pause

