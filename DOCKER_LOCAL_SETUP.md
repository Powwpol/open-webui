# 🐳 Pulsai - Configuration Docker Locale

Ce guide vous aidera à lancer Pulsai localement avec Docker.

## 📋 Prérequis

- **Docker Desktop** installé et en cours d'exécution
  - Windows: [Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Mac: [Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Linux: [Instructions d'installation](https://docs.docker.com/engine/install/)

## 🚀 Démarrage Rapide

### Windows
```bash
# Lancer Pulsai
start-docker.bat

# Ou avec des options spécifiques
start-docker.bat build   # Construire uniquement
start-docker.bat start   # Démarrer les services
start-docker.bat stop    # Arrêter les services
start-docker.bat logs    # Voir les logs
```

### Linux/Mac
```bash
# Rendre le script exécutable (première fois seulement)
chmod +x start-docker.sh

# Lancer Pulsai
./start-docker.sh

# Ou avec des options spécifiques
./start-docker.sh build   # Construire uniquement
./start-docker.sh start   # Démarrer les services
./start-docker.sh stop    # Arrêter les services
./start-docker.sh logs    # Voir les logs
```

## 🌐 Accès à l'Application

Une fois démarrée, Pulsai est accessible sur :
- **URL**: http://localhost:3000
- **Premier accès**: Vous devrez créer un compte administrateur

## ⚙️ Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine du projet pour personnaliser la configuration :

```env
# Port local (par défaut 3000)
OPEN_WEBUI_PORT=3000

# Configuration OpenAI (optionnel)
OPENAI_API_KEY=votre_cle_api
OPENAI_API_BASE_URL=

# Niveau de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### Utilisation avec Ollama

Si vous voulez utiliser Ollama localement :

1. **Installer Ollama** sur votre machine : https://ollama.ai/download

2. **Décommenter le service Ollama** dans `docker-compose.local.yaml` :
```yaml
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-local
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped
```

3. **Redémarrer les services** :
```bash
# Windows
start-docker.bat restart

# Linux/Mac
./start-docker.sh restart
```

## 📁 Structure des Données

Les données sont stockées dans :
- `./backend/data/` - Base de données SQLite, fichiers uploadés, cache

## 🛠️ Commandes Docker Utiles

```bash
# Voir les conteneurs en cours
docker ps

# Voir tous les conteneurs (y compris arrêtés)
docker ps -a

# Voir les logs en temps réel
docker logs -f open-webui-local

# Accéder au shell du conteneur
docker exec -it open-webui-local bash

# Nettoyer tout (conteneurs, volumes, images)
docker compose -f docker-compose.local.yaml down -v --rmi all
```

## 🐛 Dépannage

### Le conteneur ne démarre pas
1. Vérifiez que Docker est en cours d'exécution
2. Vérifiez que le port 3000 n'est pas déjà utilisé
3. Consultez les logs : `docker logs open-webui-local`

### Erreur de construction
1. Nettoyez le cache Docker : `docker system prune -a`
2. Relancez la construction : `docker compose -f docker-compose.local.yaml build --no-cache`

### Port déjà utilisé
Changez le port dans `docker-compose.local.yaml` :
```yaml
ports:
  - "3001:8080"  # Utiliser le port 3001 au lieu de 3000
```

### Problèmes de permissions (Linux)
```bash
# Donner les permissions au dossier de données
sudo chown -R $USER:$USER backend/data
```

## 📊 Monitoring

Pour surveiller l'utilisation des ressources :
```bash
# Statistiques en temps réel
docker stats open-webui-local

# Utilisation du disque
docker system df
```

## 🔄 Mise à Jour

Pour mettre à jour Pulsai :
```bash
# Récupérer les dernières modifications
git pull

# Reconstruire et redémarrer
# Windows
start-docker.bat clean
start-docker.bat

# Linux/Mac
./start-docker.sh clean
./start-docker.sh
```

## 💡 Conseils

- **Performance** : Allouez au moins 4GB de RAM à Docker Desktop
- **Sécurité** : En production, définissez toujours `WEBUI_SECRET_KEY` dans `.env`
- **Backup** : Sauvegardez régulièrement le dossier `backend/data`

## 📚 Documentation

- [Documentation Pulsai](https://docs.openwebui.com/)
- [GitHub Pulsai](https://github.com/open-webui/open-webui)
- [Docker Documentation](https://docs.docker.com/)

## ❓ Support

Si vous rencontrez des problèmes :
1. Consultez les logs : `docker logs open-webui-local`
2. Vérifiez la [documentation officielle](https://docs.openwebui.com/)
3. Créez une issue sur [GitHub](https://github.com/open-webui/open-webui/issues)

