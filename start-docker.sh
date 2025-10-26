#!/bin/bash

# Script de lancement pour Open WebUI avec Docker
echo "🚀 Démarrage d'Open WebUI avec Docker..."

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker Desktop."
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    exit 1
fi

# Créer le dossier de données si nécessaire
mkdir -p backend/data

# Déterminer la commande docker-compose à utiliser
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: ./start-docker.sh [OPTION]"
    echo "Options:"
    echo "  build    - Construire l'image Docker"
    echo "  start    - Démarrer les services"
    echo "  stop     - Arrêter les services"
    echo "  restart  - Redémarrer les services"
    echo "  logs     - Afficher les logs"
    echo "  clean    - Nettoyer les conteneurs et images"
    echo "  help     - Afficher cette aide"
    echo ""
    echo "Par défaut, le script va construire et démarrer les services."
}

# Traiter les arguments
case "$1" in
    build)
        echo "📦 Construction de l'image Docker..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml build
        ;;
    start)
        echo "▶️ Démarrage des services..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml up -d
        echo "✅ Open WebUI est accessible sur http://localhost:3000"
        ;;
    stop)
        echo "⏹️ Arrêt des services..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml down
        ;;
    restart)
        echo "🔄 Redémarrage des services..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml restart
        ;;
    logs)
        echo "📋 Affichage des logs..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml logs -f
        ;;
    clean)
        echo "🧹 Nettoyage des conteneurs et images..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml down -v
        docker rmi open-webui-local 2>/dev/null || true
        echo "✅ Nettoyage terminé"
        ;;
    help)
        show_help
        ;;
    *)
        # Par défaut, construire et démarrer
        echo "📦 Construction de l'image Docker..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml build
        
        echo "▶️ Démarrage des services..."
        $DOCKER_COMPOSE -f docker-compose.local.yaml up -d
        
        echo ""
        echo "✅ Open WebUI est démarré avec succès!"
        echo "🌐 Interface accessible sur: http://localhost:3000"
        echo ""
        echo "📋 Pour voir les logs: ./start-docker.sh logs"
        echo "⏹️ Pour arrêter: ./start-docker.sh stop"
        ;;
esac

