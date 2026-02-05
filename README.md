# Système d'Extraction et API pour Conventions Collectives

Système automatisé pour extraire, stocker et exposer les conventions collectives depuis ELNET via une API REST.

## 🚀 Fonctionnalités

- ✅ **Extraction automatisée** depuis ELNET avec Selenium
- ✅ **API REST** complète (FastAPI) 
- ✅ **Extraction déclenchable via API** avec monitoring temps réel
- ✅ **Détection de changements** avec tracking SHA-256
- ✅ **Base de données** SQLite ou PostgreSQL
- ✅ **Reformulation AI** (DeepSeek, optionnel)
- ✅ **Docker** (dev et production)
- ✅ **Hot reload** en développement

## 📋 Pré-requis

- Python 3.11+
- Chrome/Chromium
- Docker & Docker Compose (optionnel)
- Compte ELNET

## ⚡ Installation Rapide

### 1. Configuration

```bash
git clone <repo>
cd syntheses_ccn
cp .env.example .env
nano .env  # Ajouter ELNET_USERNAME et ELNET_PASSWORD
```

### 2. Installation locale

```bash
# Installer dépendances
pip install -r requirements.txt

# Initialiser base de données
python extract_all_to_db.py --populate-only

# Lancer API
python -m uvicorn api.main:app --reload
```

API disponible sur **http://localhost:8000/docs**

### 3. Installation Docker (recommandé)

```bash
# Development (PostgreSQL + hot reload)
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml --profile init run --rm db-init

# Production (SQLite)
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init
```

## 🌐 API

### Documentation
- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI**: http://localhost:8000/openapi.json

### Endpoints principaux

#### Conventions
```bash
GET  /api/conventions                    # Liste conventions
GET  /api/conventions/{id}               # Détails convention
GET  /api/conventions/{id}/integrale     # HTML complet + métadonnées
GET  /api/integrales                     # Conventions extraites
GET  /api/stats                          # Statistiques
```

#### Extraction (déclenchable via API)
```bash
POST /api/extract/start?end=10           # 10 premières
POST /api/extract/start?start=50&end=100 # Range 50-100
POST /api/extract/start                  # Toutes
GET  /api/extract/status                 # Progression
POST /api/extract/stop                   # Arrêter
```

#### Changements
```bash
GET  /api/changes                        # Tous changements
GET  /api/changes/unprocessed            # Non traités
GET  /api/changes/stats                  # Statistiques
POST /api/changes/{id}/mark-processed    # Marquer traité
```

## 📊 Utilisation

### Extraction via API

```python
import requests

# Démarrer extraction
r = requests.post("http://localhost:8000/api/extract/start?end=10")
print(r.json())  # {"message": "Extraction démarrée", ...}

# Surveiller progression
status = requests.get("http://localhost:8000/api/extract/status").json()
print(f"{status['progress_percent']}% - {status['current_convention']}")

# Récupérer résultats
integrales = requests.get("http://localhost:8000/api/integrales").json()
```

### Extraction via CLI

```bash
# Initialiser DB
python extract_all_to_db.py --populate-only

# Extraire 10 premières
python extract_all_to_db.py --end 10

# Range spécifique
python extract_all_to_db.py --start 50 --end 100

# Toutes
python extract_all_to_db.py
```

### Détection changements

```python
# Récupérer changements non traités
changes = requests.get("http://localhost:8000/api/changes/unprocessed").json()

for change in changes:
    # Récupérer nouvelle version
    integrale = requests.get(
        f"http://localhost:8000{change['url_integrale']}"
    ).json()
    
    # Traiter (reformuler, notifier, etc.)
    
    # Marquer comme traité
    requests.post(
        f"http://localhost:8000/api/changes/{change['change_id']}/mark-processed"
    )
```

### Reformulation (optionnel)

```bash
# Reformuler conventions extraites
python reformulate_extractions.py

# Configurer DeepSeek API key dans .env
DEEPSEEK_API_KEY=sk-...
```

## 🐳 Docker

### Development

```bash
# Démarrer (PostgreSQL + API + PgAdmin)
docker-compose -f docker-compose.dev.yml up -d

# Init DB
docker-compose -f docker-compose.dev.yml --profile init run --rm db-init

# Extraction via Docker
docker-compose -f docker-compose.dev.yml --profile extraction run --rm extractor python extract_all_to_db.py --end 10

# PgAdmin (optionnel)
docker-compose -f docker-compose.dev.yml --profile admin up -d pgadmin
# http://localhost:5050 - admin@ccn.local / admin
```

### Production

```bash
# SQLite (simple)
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init

# PostgreSQL (scalable)
echo "POSTGRES_PASSWORD=..." >> .env
docker-compose -f docker-compose.postgres.yml up -d
docker-compose -f docker-compose.postgres.yml run --rm extractor python extract_all_to_db.py --populate-only
```

### Déploiement VPS

```bash
# Cloner
git clone <repo> /opt/syntheses_ccn
cd /opt/syntheses_ccn

# Configurer
cp .env.example .env && nano .env

# Déployer
./deploy.sh

# Ou manuel
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init

# Extraction hebdomadaire (cron)
crontab -e
# 0 2 * * 0 cd /opt/syntheses_ccn && docker-compose -f docker-compose.prod.yml --profile extraction run --rm extractor
```

## 🔧 Configuration

### Variables (.env)

```env
# ELNET (requis)
ELNET_USERNAME=votre_email@exemple.com
ELNET_PASSWORD=votre_mot_de_passe

# Base de données (optionnel)
DATABASE_URL=sqlite:///./conventions.db
# PostgreSQL: DATABASE_URL=postgresql://user:password@host:5432/db

# DeepSeek (optionnel)
DEEPSEEK_API_KEY=sk-...
```

## 📁 Structure

```
.
├── api/
│   ├── main.py          # API FastAPI
│   └── database.py      # Modèles SQLAlchemy
├── extraction/
│   ├── extractor.py
│   └── elnet_connector.py
├── reformulation/
│   └── ...
├── extract_all_to_db.py      # Script extraction
├── reformulate_extractions.py
├── docker-compose*.yml        # 4 configs Docker
├── Dockerfile
├── requirements.txt
├── .env.example
├── nginx.conf
├── deploy.sh
└── README.md
```

## 🔄 Workflows

### Development local

```bash
# Terminal 1: API
python -m uvicorn api.main:app --reload

# Terminal 2: Extraction
python extract_all_to_db.py --end 10

# Navigateur
http://localhost:8000/docs
```

### Production VPS

```bash
# Déploiement initial
git clone <repo> && cd syntheses_ccn
cp .env.example .env && nano .env
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init

# Extraction hebdomadaire automatique
crontab -e
# 0 2 * * 0 cd /opt/syntheses_ccn && docker-compose -f docker-compose.prod.yml --profile extraction run --rm extractor
```

## 🧪 Tests

```bash
# Stats
curl http://localhost:8000/api/stats

# Extraction via API
curl -X POST "http://localhost:8000/api/extract/start?end=3"

# Statut
curl http://localhost:8000/api/extract/status

# Intégrale
curl http://localhost:8000/api/conventions/0/integrale

# Changements
curl http://localhost:8000/api/changes/unprocessed
```

## 📊 Base de données

### Tables
- **conventions**: Données + HTML sections + hash version
- **convention_changes**: Historique changements (SHA-256)

### Backup

```bash
# SQLite
cp conventions.db backup_$(date +%Y%m%d).db

# PostgreSQL
docker-compose exec postgres pg_dump -U ccn_user ccn > backup.sql
```

## 🔐 Sécurité

- Credentials `.env` (non versionné)
- Rate limiting Nginx
- CORS configuré
- Option API token (à activer)

## 🆘 Troubleshooting

### Port 8000 utilisé
```bash
python -m uvicorn api.main:app --port 8001
```

### Login ELNET échoue
```bash
# Vérifier credentials
cat .env
```

### Docker build échoue
```bash
docker-compose build --no-cache
```

## 📜 Licence

MIT

---

**Documentation complète**: http://localhost:8000/docs

## 📋 Pré-requis

- Python 3.11+
- Chrome/Chromium (pour extraction)
- Docker & Docker Compose (optionnel)
- Compte ELNET

## ⚡ Installation Rapide

### 1. Cloner et configurer

```bash
git clone <repo>
cd syntheses_ccn
cp .env.example .env
nano .env  # Ajouter identifiants ELNET
```

### 2. Installation locale (sans Docker)

```bash
# Installer dépendances
pip install -r requirements.txt

# Initialiser base de données
python extract_all_to_db.py --populate-only

# Lancer API
python -m uvicorn api.main:app --reload

# Extraction test (nouveau terminal)
python extract_all_to_db.py --end 10
```

### 3. Installation Docker (recommandé)

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

## 🌐 API

### Accès

- **Base URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **OpenAPI**: http://localhost:8000/openapi.json

### Endpoints principaux

#### Conventions
```bash
GET  /api/conventions              # Liste conventions
GET  /api/conventions/{id}         # Détails convention
GET  /api/conventions/{id}/integrale  # HTML complet + métadonnées
GET  /api/integrales               # Conventions extraites
GET  /api/stats                    # Statistiques
GET  /api/search?q=automobile      # Recherche
```

#### Extraction
```bash
POST /api/extract/start?end=10     # Extraire 10 premières
POST /api/extract/start?start=50&end=100  # Range 50-100
POST /api/extract/start            # Extraire toutes
GET  /api/extract/status           # Progression
POST /api/extract/stop             # Arrêter
```

#### Changements
```bash
GET  /api/changes                  # Tous changements
GET  /api/changes/unprocessed      # Non traités
GET  /api/changes/stats            # Statistiques
POST /api/changes/{id}/mark-processed  # Marquer traité
```

## 📊 Exemples d'utilisation

### Extraction via API

```python
import requests

# Démarrer extraction
requests.post("http://localhost:8000/api/extract/start?end=10")

# Surveiller progression
status = requests.get("http://localhost:8000/api/extract/status").json()
print(f"{status['progress_percent']}% - {status['current_convention']}")

# Récupérer résultats
integrales = requests.get("http://localhost:8000/api/integrales").json()
```

### Détecter changements

```python
# Récupérer changements non traités
changes = requests.get("http://localhost:8000/api/changes/unprocessed").json()

for change in changes:
    # Récupérer nouvelle version
    integrale = requests.get(
        f"http://localhost:8000{change['url_integrale']}"
    ).json()
    
    # Traiter...
    process(integrale)
    
    # Marquer comme traité
    requests.post(
        f"http://localhost:8000/api/changes/{change['change_id']}/mark-processed"
    )
```

## 🐳 Docker

### Dev (avec PostgreSQL + hot reload)

```bash
# Démarrer
docker-compose -f docker-compose.dev.yml up -d

# Init DB
docker-compose -f docker-compose.dev.yml --profile init run --rm db-init

# Extraction
docker-compose -f docker-compose.dev.yml --profile extraction run --rm extractor python extract_all_to_db.py --end 10

# PgAdmin (optionnel)
docker-compose -f docker-compose.dev.yml --profile admin up -d pgadmin
# http://localhost:5050 - admin@ccn.local / admin
```

### Production (SQLite)

```bash
# Démarrer
docker-compose -f docker-compose.prod.yml up -d

# Init DB
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init

# Extraction
docker-compose -f docker-compose.prod.yml --profile extraction run --rm extractor
```

### Production (PostgreSQL)

```bash
# Configurer mot de passe
echo "POSTGRES_PASSWORD=your_password" >> .env

# Démarrer
docker-compose -f docker-compose.postgres.yml up -d

# Init
docker-compose -f docker-compose.postgres.yml run --rm extractor python extract_all_to_db.py --populate-only
```

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# ELNET (requis)
ELNET_USERNAME=votre_email@exemple.com
ELNET_PASSWORD=votre_mot_de_passe

# Base de données (optionnel)
DATABASE_URL=sqlite:///./conventions.db
# Ou PostgreSQL:
# DATABASE_URL=postgresql://user:password@host:5432/db

# DeepSeek (optionnel, pour reformulation)
DEEPSEEK_API_KEY=sk-...
```

## 📁 Structure

```
.
├── api/
│   ├── main.py          # API FastAPI
│   └── database.py      # Modèles SQLAlchemy
├── extraction/
│   ├── extractor.py     # Extracteur principal
│   └── elnet_connector.py  # Connexion ELNET
├── reformulation/       # Reformulation AI (optionnel)
├── extract_all_to_db.py # Script extraction
├── reformulate_extractions.py  # Script reformulation
├── docker-compose.yml   # Dev simple (SQLite)
├── docker-compose.dev.yml      # Dev complet (PostgreSQL)
├── docker-compose.prod.yml     # Production (SQLite)
├── docker-compose.postgres.yml # Production (PostgreSQL)
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔄 Workflows

### Development

```bash
# Terminal 1: API
python -m uvicorn api.main:app --reload

# Terminal 2: Extraction
python extract_all_to_db.py --end 10

# Navigateur: http://localhost:8000/docs
```

### Production VPS

```bash
# Déploiement initial
git clone <repo> /opt/syntheses_ccn
cd /opt/syntheses_ccn
cp .env.example .env && nano .env
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml --profile init run --rm db-init

# Extraction hebdomadaire (cron)
crontab -e
# Ajouter: 0 2 * * 0 cd /opt/syntheses_ccn && docker-compose -f docker-compose.prod.yml --profile extraction run --rm extractor
```

## 🧪 Tests

```bash
# Stats
curl http://localhost:8000/api/stats

# Extraction test
curl -X POST "http://localhost:8000/api/extract/start?end=3"

# Statut
curl http://localhost:8000/api/extract/status

# Intégrale
curl http://localhost:8000/api/conventions/0/integrale
```

## 📝 Scripts utiles

### Windows

```bash
start.bat               # Démarrer API
start_extraction.bat    # Menu extraction
check_status.bat        # Moniteur temps réel
```

### Linux/Mac

```bash
./run_extraction.sh     # Extraction avec logs
./deploy.sh             # Déploiement production
```

## 🔐 Sécurité

- Credentials dans `.env` (non versionné)
- Rate limiting (Nginx)
- CORS configuré
- Option API token (à activer dans `api/main.py`)

## 📊 Base de données

### Tables

- **conventions**: Données conventions + HTML sections
- **convention_changes**: Historique changements détectés

### Backup

```bash
# SQLite
cp conventions.db backup_$(date +%Y%m%d).db

# PostgreSQL
docker-compose exec postgres pg_dump -U ccn_user ccn > backup.sql
```

## 🆘 Troubleshooting

### Port 8000 utilisé
```bash
# Changer port
python -m uvicorn api.main:app --port 8001
```

### Login ELNET échoue
```bash
# Vérifier credentials
cat .env

# Test extraction
python -c "from extraction.elnet_connector import ElnetConnector; c = ElnetConnector('user', 'pass'); c.setup_driver(); print(c.login())"
```

### Docker build échoue
```bash
# Build sans cache
docker-compose build --no-cache
```

## 📜 Licence

MIT

## 👥 Contributeurs

Votre nom ici

---

**Documentation API complète**: http://localhost:8000/docs
