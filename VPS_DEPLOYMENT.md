# Déploiement VPS avec Auto-Update GitHub

Ce guide explique comment déployer sur VPS avec mise à jour automatique depuis GitHub.

## Principe

À chaque `docker-compose up --build`, le code est récupéré depuis GitHub :
1. Dockerfile.vps clone le repository
2. Build l'image avec le code le plus récent
3. Démarre l'application

## Installation initiale

### 1. Connexion VPS

```bash
ssh user@your-vps-ip
```

### 2. Installer Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Se reconnecter
exit
ssh user@your-vps-ip
```

### 3. Créer répertoire

```bash
mkdir -p /opt/syntheses_ccn
cd /opt/syntheses_ccn
```

### 4. Télécharger fichiers config

```bash
# Télécharger docker-compose et Dockerfile
wget https://raw.githubusercontent.com/rose0110/syntheses_ccn/main/docker-compose.vps.yml
wget https://raw.githubusercontent.com/rose0110/syntheses_ccn/main/Dockerfile.vps
wget https://raw.githubusercontent.com/rose0110/syntheses_ccn/main/deploy_vps.sh

chmod +x deploy_vps.sh
```

### 5. Configurer .env

```bash
nano .env
```

Ajouter :
```env
ELNET_USERNAME=votre_email@exemple.com
ELNET_PASSWORD=votre_mot_de_passe
DATABASE_URL=sqlite:///./conventions.db
```

### 6. Déployer

```bash
./deploy_vps.sh
```

## Mise à jour (automatique)

### Build et redéploiement

```bash
cd /opt/syntheses_ccn
./deploy_vps.sh
```

Cette commande :
1. Clone la dernière version depuis GitHub
2. Build l'image
3. Redémarre l'application

### Manuel

```bash
# Rebuild (clone GitHub auto)
docker-compose -f docker-compose.vps.yml build --no-cache

# Redémarrer
docker-compose -f docker-compose.vps.yml down
docker-compose -f docker-compose.vps.yml up -d
```

## Extraction hebdomadaire

### Configurer cron

```bash
crontab -e
```

Ajouter :
```bash
# Extraction tous les dimanches à 2h
0 2 * * 0 cd /opt/syntheses_ccn && docker-compose -f docker-compose.vps.yml --profile extraction run --rm extractor >> /opt/syntheses_ccn/logs/cron_extraction.log 2>&1
```

## Commandes utiles

### Logs

```bash
# API
docker-compose -f docker-compose.vps.yml logs -f api

# Extraction
docker-compose -f docker-compose.vps.yml --profile extraction logs extractor
```

### Extraction manuelle

```bash
# 10 premières
docker-compose -f docker-compose.vps.yml --profile extraction run --rm extractor python extract_all_to_db.py --end 10

# Toutes
docker-compose -f docker-compose.vps.yml --profile extraction run --rm extractor
```

### Stats

```bash
curl http://localhost:8000/api/stats
```

### Backup DB

```bash
cp conventions.db backup_$(date +%Y%m%d).db
```

## Nginx (optionnel)

### Démarrer Nginx

```bash
docker-compose -f docker-compose.vps.yml --profile nginx up -d nginx
```

### Configuration domaine

Modifier `nginx.conf` :
```nginx
server_name votre-domaine.com;
```

### SSL (Let's Encrypt)

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Générer certificat
sudo certbot --nginx -d votre-domaine.com

# Renouvellement auto
sudo certbot renew --dry-run
```

## Monitoring

### Health check

```bash
curl http://localhost:8000/
```

### Vérifier containers

```bash
docker ps
docker-compose -f docker-compose.vps.yml ps
```

### Resources

```bash
docker stats
```

## Troubleshooting

### API ne démarre pas

```bash
# Logs
docker-compose -f docker-compose.vps.yml logs api

# Rebuild complet
docker-compose -f docker-compose.vps.yml build --no-cache
docker-compose -f docker-compose.vps.yml up -d
```

### Port 8000 déjà utilisé

```bash
# Voir processus
sudo lsof -i :8000

# Ou changer port dans docker-compose.vps.yml
ports:
  - "8001:8000"
```

### Extraction échoue

```bash
# Vérifier .env
docker-compose -f docker-compose.vps.yml exec api cat .env

# Test extraction
docker-compose -f docker-compose.vps.yml --profile extraction run --rm extractor python extract_all_to_db.py --end 1
```

## Workflow complet

```bash
# 1. Déploiement initial
ssh user@vps
cd /opt/syntheses_ccn
./deploy_vps.sh

# 2. Vérifier
curl http://localhost:8000/api/stats

# 3. Extraction test
docker-compose -f docker-compose.vps.yml --profile extraction run --rm extractor python extract_all_to_db.py --end 3

# 4. Configurer cron
crontab -e
# Ajouter ligne extraction hebdo

# 5. Monitoring
docker-compose -f docker-compose.vps.yml logs -f
```

## Architecture

```
VPS
├── Dockerfile.vps → Clone GitHub → Build
├── docker-compose.vps.yml → Orchestration
├── deploy_vps.sh → Script auto-update
├── .env → Credentials
├── conventions.db → Base de données
└── logs/ → Logs
```

## Avantages

- ✅ Code toujours à jour (clone GitHub)
- ✅ Déploiement en 1 commande
- ✅ Rollback facile (rebuild version précédente)
- ✅ Pas de git pull manuel
- ✅ CI/CD intégré

## Sécurité

- .env non versionné
- Credentials protégés
- Isolation Docker
- Rate limiting Nginx
- HTTPS via Let's Encrypt
