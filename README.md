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
git clone https://github.com/rose0110/syntheses_ccn.git
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

**Conventions & Recherche**
| Méthode | Route | Description |
|:---|:---|:---|
| `GET` | `/api/conventions` | Liste toutes les conventions (filtres: `skip`, `limit`, `status`, `idcc`) |
| `GET` | `/api/conventions/{id}` | Détails d'une convention (métadonnées, sections, TOC) |
| `GET` | `/api/conventions/idcc/{idcc}` | Retrouver une convention par son code IDCC (ex: "0044") |
| `GET` | `/api/conventions/{id}/integrale` | Alias vers les détails complets |
| `GET` | `/api/conventions/{id}/sections` | Liste des sections HTML uniquement |
| `GET` | `/api/conventions/{id}/toc` | Table des matières (JSON) |
| `GET` | `/api/search?q=...` | Recherche (insensible à la casse) dans titre ou IDCC |
| `GET` | `/api/stats` | Statistiques globales (total, extraites, erreurs...) |

**Extraction (Pilotage)**
| Méthode | Route | Description |
|:---|:---|:---|
| `POST` | `/api/extract/start` | Lancer une extraction (params: `start`, `end`) |
| `GET` | `/api/extract/status` | Suivi temps réel (progression, logs) |
| `POST` | `/api/extract/stop` | Arrêter l'extraction en cours |

**Suivi des Changements (Diff)**
| Méthode | Route | Description |
|:---|:---|:---|
| `GET` | `/api/changes` | Historique des changements détectés |
| `GET` | `/api/changes/unprocessed` | Changements en attente de traitement |
| `GET` | `/api/changes/stats` | Stats des changements |
| `POST` | `/api/changes/{id}/mark-processed` | Marquer un changement comme traité |

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

1. **Installation**
   ```bash
   git clone <repo> /opt/syntheses_ccn
   cd /opt/syntheses_ccn
   cp .env.example .env
   nano .env # Configurer ELNET_USERNAME, ELNET_PASSWORD, etc.
   ```

2. **Lancement de l'API**
   ```bash
   # Lancer le service API (en mode détaché)
   docker-compose -f docker-compose.vps.yml up -d --remove-orphans
   ```

3. **Initialisation de la Base de Données**
   Cette étape crée les tables et importe la liste des conventions.
   ```bash
   docker-compose -f docker-compose.vps.yml --profile init up db-init
   ```

4. **Lancement de l'Extraction**
   ```bash
   # Lancer l'extraction complète en arrière-plan
   docker-compose -f docker-compose.vps.yml --profile extraction up -d extractor

   # Ou tester sur quelques conventions (ex: les 5 premières)
   docker-compose -f docker-compose.vps.yml run --rm extractor python extract_all_to_db.py --start 0 --end 5
   ```

5. **Mise à jour du code (Déploiement Continu)**
   Grâce au montage dynamique du volume, pas besoin de reconstruire l'image Docker à chaque changement.
   ```bash
   # 1. Récupérer le dernier code
   git pull

   # 2. Redémarrer l'API pour prendre en compte les changements Python
   docker-compose -f docker-compose.vps.yml restart api
   ```

### Troubleshooting VPS

**Erreur "unable to open database file"**
Si Docker a créé `conventions.db` ou `syntheses.db` comme des dossiers au lieu de fichiers :
```bash
docker-compose -f docker-compose.vps.yml down
rm -rf conventions.db syntheses.db
docker-compose -f docker-compose.vps.yml up -d
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
