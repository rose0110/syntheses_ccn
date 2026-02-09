#!/bin/bash

# Script de déploiement VPS avec auto-update depuis GitHub

set -e

echo "================================"
echo "  Déploiement CCN VPS"
echo "================================"

# 1. Backup DB si existe
if [ -f "conventions.db" ]; then
    echo "📦 Backup base de données..."
    cp conventions.db "backup_$(date +%Y%m%d_%H%M%S).db"
fi

# 2. Build (clone GitHub automatique)
echo "🔨 Build depuis GitHub..."
docker-compose -f docker-compose.vps.yml build --no-cache

# 3. Arrêter anciens containers
echo "🛑 Arrêt containers..."
docker-compose -f docker-compose.vps.yml down

# 4. Démarrer
echo "🚀 Démarrage..."
docker-compose -f docker-compose.vps.yml up -d

# 5. Init DB si vide
echo "📊 Vérification DB..."
if [ ! -f "conventions.db" ]; then
    echo "Initialisation DB..."
    docker-compose -f docker-compose.vps.yml --profile init run --rm db-init
fi

# 6. Health check
echo "🏥 Health check..."
sleep 10
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ API opérationnelle"
else
    echo "❌ Erreur API"
    docker-compose -f docker-compose.vps.yml logs api
    exit 1
fi

echo ""
echo "================================"
echo "  ✅ Déploiement réussi"
echo "================================"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""
echo "Commandes utiles:"
echo "  docker-compose -f docker-compose.vps.yml logs -f api"
echo "  docker-compose -f docker-compose.vps.yml --profile extraction run --rm extractor"
echo ""
