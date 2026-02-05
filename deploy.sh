#!/bin/bash
# Script de déploiement automatique pour VPS production

set -e  # Exit on error

echo "=== Déploiement CCN API - Production ==="
echo "Date: $(date)"

# Variables
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="backups"

# 1. Pull dernières modifications
echo "1. Pulling latest code..."
git pull origin main

# 2. Backup database
echo "2. Backing up database..."
mkdir -p $BACKUP_DIR
if [ -f "conventions.db" ]; then
    cp conventions.db "$BACKUP_DIR/conventions_$(date +%Y%m%d_%H%M%S).db"
    echo "   ✓ Database backed up"
fi

# 3. Build nouvelle image
echo "3. Building Docker image..."
docker-compose -f $COMPOSE_FILE build

# 4. Arrêter ancienne version
echo "4. Stopping old containers..."
docker-compose -f $COMPOSE_FILE down

# 5. Démarrer nouvelle version
echo "5. Starting new containers..."
docker-compose -f $COMPOSE_FILE up -d api

# 6. Attendre que l'API soit prête
echo "6. Waiting for API to be ready..."
sleep 5

# 7. Health check
echo "7. Health check..."
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "   ✓ API is healthy"
else
    echo "   ✗ API health check failed!"
    echo "   Rolling back..."
    
    # Rollback
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE up -d api
    
    exit 1
fi

# 8. Nettoyage
echo "8. Cleaning up..."
docker system prune -f

echo ""
echo "=== Déploiement terminé avec succès ==="
echo "API accessible sur: http://localhost:8000"
