#!/bin/sh
# ============================================================
# entrypoint.sh — Point d'entrée Docker (API + Scraper)
# Restaure automatiquement elnet.db depuis database.sql(.gz)
# si le fichier DB est absent (ex : premier git pull + up)
# ============================================================

DB_PATH="/app/data/elnet.db"
SQL_GZ="/app/database.sql.gz"
SQL_RAW="/app/database.sql"

echo "🔍 Vérification de la base de données..."
mkdir -p /app/data

if [ ! -f "$DB_PATH" ]; then
    echo "⚠️  elnet.db introuvable — tentative de restauration..."

    if [ -f "$SQL_GZ" ]; then
        echo "📥 Restauration depuis database.sql.gz ..."
        gunzip -c "$SQL_GZ" | sqlite3 "$DB_PATH"
        echo "✅ Base de données restaurée depuis .gz ($(du -sh $DB_PATH | cut -f1))"

    elif [ -f "$SQL_RAW" ]; then
        echo "📥 Restauration depuis database.sql ..."
        sqlite3 "$DB_PATH" < "$SQL_RAW"
        echo "✅ Base de données restaurée depuis .sql ($(du -sh $DB_PATH | cut -f1))"

    else
        echo "⚠️  Aucun dump SQL trouvé. La BDD sera vide."
        echo "   Lance : python export_db.py  (en local) puis git push"
    fi
else
    echo "✅ Base de données existante ($(du -sh $DB_PATH | cut -f1))"
fi

echo "🚀 Démarrage..."
exec "$@"
