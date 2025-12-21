# Guide de Déploiement sur VPS 🚀

Ce guide vous explique comment déployer le système de Trading IA sur un VPS (Ubuntu 22.04 recommandé).

## 📋 Table des Matières

1. [Prérequis VPS](#prérequis-vps)
2. [Installation Initiale](#installation-initiale)
3. [Configuration Backend](#configuration-backend)
4. [Configuration Frontend](#configuration-frontend)
5. [Base de Données PostgreSQL](#base-de-données-postgresql)
6. [Services Systemd](#services-systemd)
7. [Nginx Reverse Proxy](#nginx-reverse-proxy)
8. [SSL/HTTPS (Let's Encrypt)](#sslhttps)
9. [Monitoring & Logs](#monitoring--logs)
10. [Déploiement avec Docker](#déploiement-avec-docker-alternative)

---

## Prérequis VPS

### Spécifications Minimales
- **OS**: Ubuntu 22.04 LTS (recommandé)
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Stockage**: 40 GB SSD
- **Fournisseurs**: DigitalOcean, Linode, Vultr, AWS EC2

### Coûts Estimés
- DigitalOcean: $24/mois (2 vCPU, 4GB RAM)
- Linode: $24/mois
- Vultr: $24/mois
- AWS EC2 t3.medium: ~$30/mois

---

## Installation Initiale

### 1. Connexion SSH au VPS

```bash
ssh root@your-vps-ip
```

### 2. Mise à Jour du Système

```bash
apt update && apt upgrade -y
```

### 3. Création Utilisateur Non-Root

```bash
# Créer utilisateur
adduser trading
usermod -aG sudo trading

# Copier clés SSH
rsync --archive --chown=trading:trading ~/.ssh /home/trading

# Se connecter comme nouvel utilisateur
su - trading
```

### 4. Installation des Dépendances Système

```bash
# Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# PostgreSQL 15
sudo apt install -y postgresql postgresql-contrib

# Nginx
sudo apt install -y nginx

# Git
sudo apt install -y git

# Autres outils
sudo apt install -y build-essential curl wget certbot python3-certbot-nginx
```

---

## Configuration Backend

### 1. Cloner le Projet

```bash
cd /home/trading
git clone <your-repo-url> trading-ai
cd trading-ai/backend
```

### 2. Environnement Virtuel Python

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration Variables d'Environnement

```bash
# Créer .env
nano .env
```

Contenu `.env`:
```bash
# App Config
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=postgresql://trading_user:strong_password@localhost:5432/trading_ai_db

# API Keys
XAI_API_KEY=xai-your-grok-api-key-here
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-secret
TWITTER_BEARER_TOKEN=your-bearer-token
GOOGLE_SEARCH_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Trading Config
TRADING_MODE=paper  # paper ou live
INITIAL_CAPITAL=10000
MAX_POSITIONS=3
MAX_DRAWDOWN=20
STOP_LOSS_DEFAULT=5
TAKE_PROFIT_DEFAULT=10

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/trading-ai/backend.log
```

### 4. Test du Backend

```bash
# Activer venv
source venv/bin/activate

# Lancer temporairement
uvicorn main:app --host 0.0.0.0 --port 8000

# Tester
curl http://localhost:8000/api/health
```

---

## Configuration Frontend

### 1. Build Production

```bash
cd /home/trading/trading-ai/frontend

# Créer .env.production
nano .env.production
```

Contenu `.env.production`:
```bash
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
```

```bash
# Installer dépendances
npm install

# Build production
npm run build

# Les fichiers sont dans dist/
```

### 2. Déplacer Build vers Nginx

```bash
sudo mkdir -p /var/www/trading-ai
sudo cp -r dist/* /var/www/trading-ai/
sudo chown -R www-data:www-data /var/www/trading-ai
```

---

## Base de Données PostgreSQL

### 1. Configuration PostgreSQL

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Dans psql:
CREATE DATABASE trading_ai_db;
CREATE USER trading_user WITH ENCRYPTED PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE trading_ai_db TO trading_user;

# Donner permissions sur schéma public
\c trading_ai_db
GRANT ALL ON SCHEMA public TO trading_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading_user;

\q
```

### 2. Migrations Alembic

```bash
cd /home/trading/trading-ai/backend
source venv/bin/activate

# Générer migration
alembic revision --autogenerate -m "Initial schema"

# Appliquer migration
alembic upgrade head
```

### 3. Backup Automatique PostgreSQL

```bash
# Créer script backup
sudo nano /usr/local/bin/backup-trading-db.sh
```

Contenu:
```bash
#!/bin/bash
BACKUP_DIR="/home/trading/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U trading_user trading_ai_db > $BACKUP_DIR/trading_ai_$DATE.sql

# Garder seulement 7 derniers jours
find $BACKUP_DIR -name "trading_ai_*.sql" -mtime +7 -delete
```

```bash
# Rendre exécutable
sudo chmod +x /usr/local/bin/backup-trading-db.sh

# Ajouter au crontab (tous les jours à 2h)
crontab -e
# Ajouter:
0 2 * * * /usr/local/bin/backup-trading-db.sh
```

---

## Services Systemd

### 1. Service Backend (Uvicorn)

```bash
sudo nano /etc/systemd/system/trading-backend.service
```

Contenu:
```ini
[Unit]
Description=Trading AI Backend (FastAPI)
After=network.target postgresql.service

[Service]
Type=simple
User=trading
Group=trading
WorkingDirectory=/home/trading/trading-ai/backend
Environment="PATH=/home/trading/trading-ai/backend/venv/bin"
ExecStart=/home/trading/trading-ai/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/trading-ai/backend.log
StandardError=append:/var/log/trading-ai/backend-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 2. Créer Dossier Logs

```bash
sudo mkdir -p /var/log/trading-ai
sudo chown trading:trading /var/log/trading-ai
```

### 3. Activer et Démarrer Service

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable trading-backend

# Démarrer service
sudo systemctl start trading-backend

# Vérifier status
sudo systemctl status trading-backend

# Voir logs
sudo journalctl -u trading-backend -f
```

---

## Nginx Reverse Proxy

### 1. Configuration Nginx

```bash
sudo nano /etc/nginx/sites-available/trading-ai
```

Contenu:
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    return 301 https://$server_name$request_uri;
}

# Backend API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Backend proxy
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

# Frontend
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/trading-ai;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. Activer Configuration

```bash
# Créer lien symbolique
sudo ln -s /etc/nginx/sites-available/trading-ai /etc/nginx/sites-enabled/

# Tester configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

---

## SSL/HTTPS

### Configuration Let's Encrypt (Certbot)

```bash
# Obtenir certificats SSL (avant d'activer HTTPS dans nginx)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Renouvellement automatique (déjà configuré par certbot)
# Tester renouvellement
sudo certbot renew --dry-run
```

---

## Monitoring & Logs

### 1. Logs Backend

```bash
# Logs en temps réel
sudo journalctl -u trading-backend -f

# Logs des 100 dernières lignes
sudo journalctl -u trading-backend -n 100

# Logs d'aujourd'hui
sudo journalctl -u trading-backend --since today

# Logs fichier
tail -f /var/log/trading-ai/backend.log
```

### 2. Logs Nginx

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### 3. Monitoring Système

```bash
# Installer htop
sudo apt install htop

# Monitoring
htop

# Disk usage
df -h

# Mémoire
free -h
```

### 4. Script de Santé

```bash
nano /home/trading/health-check.sh
```

Contenu:
```bash
#!/bin/bash

echo "=== Trading AI Health Check ==="
echo ""

# Backend service
echo "Backend Service:"
sudo systemctl is-active trading-backend
echo ""

# Database
echo "PostgreSQL:"
sudo systemctl is-active postgresql
echo ""

# Nginx
echo "Nginx:"
sudo systemctl is-active nginx
echo ""

# Disk space
echo "Disk Usage:"
df -h | grep -E "/$|/home"
echo ""

# Memory
echo "Memory:"
free -h
echo ""

# Backend API
echo "Backend API Health:"
curl -s http://localhost:8000/api/health | jq
```

```bash
chmod +x /home/trading/health-check.sh
```

---

## Déploiement avec Docker (Alternative)

### 1. Dockerfile Backend

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Dockerfile Frontend

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: trading_ai_db
      POSTGRES_USER: trading_user
      POSTGRES_PASSWORD: strong_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://trading_user:strong_password@db:5432/trading_ai_db
    env_file:
      - ./backend/.env
    depends_on:
      - db
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always

volumes:
  postgres_data:
```

### 4. Déployer avec Docker

```bash
# Build et lancer
docker-compose up -d

# Voir logs
docker-compose logs -f

# Arrêter
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## Commandes Utiles

### Redémarrage Services

```bash
# Backend
sudo systemctl restart trading-backend

# Nginx
sudo systemctl restart nginx

# PostgreSQL
sudo systemctl restart postgresql

# Tout redémarrer
sudo systemctl restart trading-backend nginx postgresql
```

### Mise à Jour du Code

```bash
cd /home/trading/trading-ai

# Backend
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart trading-backend

# Frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/trading-ai/
sudo systemctl reload nginx
```

### Rollback

```bash
# Revenir à commit précédent
git log --oneline  # Voir commits
git checkout <commit-hash>
sudo systemctl restart trading-backend
```

---

## Sécurité

### Firewall (UFW)

```bash
# Installer UFW
sudo apt install ufw

# Configurer
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Vérifier
sudo ufw status
```

### Fail2Ban (Protection SSH)

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Support

En cas de problème:
1. Vérifier logs: `sudo journalctl -u trading-backend -n 100`
2. Vérifier service: `sudo systemctl status trading-backend`
3. Vérifier santé: `/home/trading/health-check.sh`
4. Consulter documentation API: `https://api.yourdomain.com/docs`

---

**Déploiement créé avec ❤️ et Claude Code**
