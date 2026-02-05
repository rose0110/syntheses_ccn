# Système d'Extraction et API pour Conventions Collectives

Système automatisé pour extraire, stocker et exposer les conventions collectives depuis ELNET via une API REST.

## Fonctionnalités

- Extraction automatisée depuis ELNET avec Selenium
- API REST complète (FastAPI) 
- Extraction déclenchable via API avec monitoring temps réel
- Détection de changements avec tracking SHA-256
- Base de données SQLite ou PostgreSQL
- Reform

ulation AI (DeepSeek, optionnel)
- Docker (dev et production)
- Hot reload en développement

## Pré-requis

- Python 3.11+
- Chrome/Chromium
- Docker & Docker Compose (optionnel)
- Compte ELNET

## Installation

### Configuration

```bash
git clone <repo>
cd syntheses_ccn
cp .env.example .env
nano .env  # Ajouter ELNET_USERNAME et ELNET_PASSWORD
```

### Installation locale

```bash
pip install -r requirements.txt
python extract_all_to_db.py --populate-only
python -m uvicorn api.main:app --reload
```

API disponible sur http://localhost:8000/docs

### Installation Docker

```bash
# Development
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml --profile init run --rm db-init

# Production
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init
```

## API

Documentation: http://localhost:8000/docs

### Endpoints

**Conventions**
```
GET  /api/conventions
GET  /api/conventions/{id}
GET  /api/conventions/{id}/integrale
GET  /api/integrales
GET  /api/stats
```

**Extraction**
```
POST /api/extract/start?end=10
POST /api/extract/start?start=50&end=100
GET  /api/extract/status
POST /api/extract/stop
```

**Changements**
```
GET  /api/changes
GET  /api/changes/unprocessed
GET  /api/changes/stats
POST /api/changes/{id}/mark-processed
```

## Utilisation

### Extraction via API

```python
import requests

# Démarrer
requests.post("http://localhost:8000/api/extract/start?end=10")

# Surveiller
status = requests.get("http://localhost:8000/api/extract/status").json()
print(f"{status['progress_percent']}%")

# Résultats
integrales = requests.get("http://localhost:8000/api/integrales").json()
```

### Extraction via CLI

```bash
python extract_all_to_db.py --populate-only
python extract_all_to_db.py --end 10
python extract_all_to_db.py --start 50 --end 100
```

### Détection changements

```python
changes = requests.get("http://localhost:8000/api/changes/unprocessed").json()

for change in changes:
    integrale = requests.get(f"http://localhost:8000{change['url_integrale']}").json()
    process(integrale)
    requests.post(f"http://localhost:8000/api/changes/{change['change_id']}/mark-processed")
```

## Docker

### Development

```bash
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml --profile init run --rm db-init
docker-compose -f docker-compose.dev.yml --profile extraction run --rm extractor python extract_all_to_db.py --end 10
```

### Production

```bash
# SQLite
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init

# PostgreSQL
echo "POSTGRES_PASSWORD=..." >> .env
docker-compose -f docker-compose.postgres.yml up -d
docker-compose -f docker-compose.postgres.yml run --rm extractor python extract_all_to_db.py --populate-only
```

### Déploiement VPS

```bash
git clone <repo> /opt/syntheses_ccn
cd /opt/syntheses_ccn
cp .env.example .env && nano .env
./deploy.sh

# Extraction hebdomadaire (cron)
crontab -e
# 0 2 * * 0 cd /opt/syntheses_ccn && docker-compose -f docker-compose.prod.yml --profile extraction run --rm extractor
```

## Configuration

Variables (.env):

```env
ELNET_USERNAME=votre_email@exemple.com
ELNET_PASSWORD=votre_mot_de_passe
DATABASE_URL=sqlite:///./conventions.db
DEEPSEEK_API_KEY=sk-...
```

## Structure

```
.
├── api/
│   ├── main.py
│   └── database.py
├── extraction/
│   ├── extractor.py
│   └── elnet_connector.py
├── reformulation/
├── extract_all_to_db.py
├── reformulate_extractions.py
├── docker-compose*.yml
├── Dockerfile
└── requirements.txt
```

## Tests

```bash
curl http://localhost:8000/api/stats
curl -X POST "http://localhost:8000/api/extract/start?end=3"
curl http://localhost:8000/api/extract/status
curl http://localhost:8000/api/conventions/0/integrale
```

## Base de données

Tables:
- **conventions**: Données + HTML sections + hash version
- **convention_changes**: Historique changements (SHA-256)

Backup:
```bash
cp conventions.db backup_$(date +%Y%m%d).db
docker-compose exec postgres pg_dump -U ccn_user ccn > backup.sql
```

## Sécurité

- Credentials .env (non versionné)
- Rate limiting Nginx
- CORS configuré

## Troubleshooting

### Port 8000 utilisé
```bash
python -m uvicorn api.main:app --port 8001
```

### Login ELNET échoue
```bash
cat .env
```

### Docker build échoue
```bash
docker-compose build --no-cache
```

## Licence

MIT
