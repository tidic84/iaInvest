# Guide d'Installation Détaillé 📦

Ce guide vous accompagne pas à pas dans l'installation complète du système de Trading IA Auto-Apprenant.

## 📋 Table des Matières

1. [Prérequis Système](#prérequis-système)
2. [Installation Backend](#installation-backend)
3. [Installation Frontend](#installation-frontend)
4. [Base de Données](#base-de-données)
5. [Obtention des Clés API](#obtention-des-clés-api)
6. [Premier Lancement](#premier-lancement)
7. [Vérification Installation](#vérification-installation)
8. [Troubleshooting](#troubleshooting)

---

## Prérequis Système

### Systèmes d'Exploitation Supportés

- **Linux**: Ubuntu 20.04+, Debian 11+, CentOS 8+
- **macOS**: 11 (Big Sur) ou supérieur
- **Windows**: 10/11 avec WSL2 (recommandé) ou natif

### Logiciels Requis

#### Python 3.11+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**macOS (avec Homebrew):**
```bash
brew install python@3.11
```

**Windows:**
Télécharger depuis [python.org](https://www.python.org/downloads/)

**Vérification:**
```bash
python3.11 --version
# Devrait afficher: Python 3.11.x
```

#### Node.js 18+

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**macOS:**
```bash
brew install node@18
```

**Windows:**
Télécharger depuis [nodejs.org](https://nodejs.org/)

**Vérification:**
```bash
node --version  # v18.x.x ou supérieur
npm --version   # 9.x.x ou supérieur
```

#### PostgreSQL 15+ (Production) ou SQLite (Développement)

**PostgreSQL - Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**PostgreSQL - macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**PostgreSQL - Windows:**
Télécharger depuis [postgresql.org](https://www.postgresql.org/download/)

**SQLite (inclus avec Python):**
```bash
python3.11 -c "import sqlite3; print(sqlite3.version)"
```

#### Git

**Linux:**
```bash
sudo apt install git  # Ubuntu/Debian
sudo yum install git  # CentOS/RHEL
```

**macOS:**
```bash
brew install git
```

**Windows:**
Télécharger depuis [git-scm.com](https://git-scm.com/)

**Vérification:**
```bash
git --version
```

---

## Installation Backend

### 1. Cloner le Projet

```bash
# Cloner le repository
git clone <your-repo-url> trading-ai
cd trading-ai
```

### 2. Créer Environnement Virtuel Python

```bash
cd backend

# Créer venv
python3.11 -m venv venv

# Activer venv
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Vérifier activation (devrait montrer le chemin du venv)
which python
```

### 3. Installer Dépendances Python

```bash
# Upgrade pip
pip install --upgrade pip

# Installer toutes les dépendances
pip install -r requirements.txt

# Vérifier installation
pip list
```

**Dépendances principales installées:**
- fastapi (API framework)
- uvicorn (ASGI server)
- sqlalchemy (ORM)
- alembic (migrations)
- psycopg2-binary (PostgreSQL driver)
- yfinance (market data stocks)
- ccxt (market data crypto)
- tweepy (Twitter API)
- openai (Grok API compatible)
- pandas, numpy (data processing)

### 4. Configuration Variables d'Environnement

```bash
# Copier template
cp .env.example .env

# Éditer .env
nano .env  # ou vim, code, etc.
```

**Configuration minimale .env:**
```bash
# App
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=changez-cette-cle-en-production

# Database (SQLite pour dev)
DATABASE_URL=sqlite:///./trading_ai.db

# API Keys (OBLIGATOIRE)
GROK_API_KEY=xai-votre-cle-ici

# Trading
TRADING_MODE=paper
INITIAL_CAPITAL=10000

# Server
HOST=0.0.0.0
PORT=8000
```

**Pour obtenir les clés API, voir section [Obtention des Clés API](#obtention-des-clés-api)**

### 5. Initialiser Base de Données

#### Option A: SQLite (Développement)

```bash
# Database sera créée automatiquement
# Générer migration initiale
alembic revision --autogenerate -m "Initial schema"

# Appliquer migrations
alembic upgrade head

# Vérifier
ls -la *.db  # Devrait montrer trading_ai.db
```

#### Option B: PostgreSQL (Production)

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Dans psql:
CREATE DATABASE trading_ai_db;
CREATE USER trading_user WITH ENCRYPTED PASSWORD 'votre-mot-de-passe';
GRANT ALL PRIVILEGES ON DATABASE trading_ai_db TO trading_user;
\q

# Modifier .env
DATABASE_URL=postgresql://trading_user:votre-mot-de-passe@localhost:5432/trading_ai_db

# Générer et appliquer migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### 6. Test Backend

```bash
# Lancer serveur de développement
uvicorn main:app --reload

# Dans un autre terminal, tester API
curl http://localhost:8000/api/health

# Devrait retourner:
# {"status": "healthy", "version": "1.0.0"}
```

**Accéder à la documentation interactive:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Installation Frontend

### 1. Naviguer au Dossier Frontend

```bash
cd ../frontend  # depuis backend/
```

### 2. Installer Dépendances Node.js

```bash
# Installer packages
npm install

# Ou avec yarn
yarn install
```

**Dépendances principales installées:**
- react, react-dom
- typescript
- vite (build tool)
- tailwindcss (styling)
- chart.js, react-chartjs-2 (graphiques)
- axios (HTTP client)
- date-fns (formatage dates)

### 3. Configuration Variables d'Environnement

```bash
# Créer .env.development
nano .env.development
```

**Contenu .env.development:**
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_MODE=development
```

### 4. Lancer Serveur de Développement

```bash
npm run dev

# Ou avec yarn
yarn dev
```

**Devrait afficher:**
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 5. Ouvrir dans Navigateur

Ouvrir http://localhost:5173/ dans votre navigateur.

**Vous devriez voir le Dashboard Trading AI.**

---

## Base de Données

### Structure des Tables

Après `alembic upgrade head`, 5 tables sont créées:

1. **trades**
   - Historique complet de tous les trades
   - Colonnes: id, trade_number, timestamp, action, symbol, quantity, price, pnl, status, etc.

2. **reflections**
   - Auto-réflexions de l'IA après chaque 5 trades
   - Colonnes: id, timestamp, trades_analyzed, mistakes (JSON), successes (JSON), new_rules (JSON)

3. **learned_rules**
   - Règles apprises par l'IA au fil du temps
   - Colonnes: id, rule, created_at, from_reflection_id

4. **portfolio_snapshots**
   - Snapshots périodiques du portfolio pour graphiques
   - Colonnes: id, timestamp, total_value, cash, positions (JSON), total_pnl

5. **strategy_history**
   - Historique des paramètres de stratégie
   - Colonnes: id, timestamp, parameters (JSON), reason

### Vérifier Tables (PostgreSQL)

```bash
sudo -u postgres psql trading_ai_db

\dt  # Liste toutes les tables
\d trades  # Détails de la table trades
SELECT COUNT(*) FROM trades;
\q
```

### Vérifier Tables (SQLite)

```bash
sqlite3 trading_ai.db

.tables  -- Liste toutes les tables
.schema trades  -- Structure de la table trades
SELECT COUNT(*) FROM trades;
.quit
```

---

## Obtention des Clés API

### 1. Grok API (xAI) - OBLIGATOIRE

**Coût:** ~$4-6/semaine en mode paper trading

**Étapes:**
1. Aller sur https://x.ai/api
2. Se connecter ou créer compte
3. Créer nouveau projet
4. Générer clé API
5. Copier clé (commence par `xai-`)

**Ajouter à .env:**
```bash
GROK_API_KEY=xai-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROK_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-beta
```

**Test:**
```bash
curl https://api.x.ai/v1/models \
  -H "Authorization: Bearer $GROK_API_KEY"
```

### 2. Twitter/X API - OPTIONNEL

**Coût:** Gratuit (limites: 50 requêtes/15min)

**Étapes:**
1. Aller sur https://developer.twitter.com/en/portal/dashboard
2. Créer Developer Account
3. Créer App
4. Générer Bearer Token

**Ajouter à .env:**
```bash
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Test:**
```bash
curl "https://api.twitter.com/2/tweets/search/recent?query=bitcoin&max_results=10" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

### 3. Google Custom Search API - OPTIONNEL

**Coût:** Gratuit (100 requêtes/jour)

**Étapes:**
1. Aller sur https://developers.google.com/custom-search/v1/introduction
2. Créer projet Google Cloud
3. Activer Custom Search API
4. Créer clé API
5. Créer Search Engine: https://programmablesearchengine.google.com/

**Ajouter à .env:**
```bash
GOOGLE_SEARCH_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SEARCH_ENGINE_ID=xxxxxxxxxxxxxxxxx
```

**Test:**
```bash
curl "https://www.googleapis.com/customsearch/v1?key=$GOOGLE_SEARCH_API_KEY&cx=$GOOGLE_SEARCH_ENGINE_ID&q=bitcoin+news"
```

### 4. Binance API - OPTIONNEL (Live Trading Crypto)

**⚠️ Seulement si vous voulez trader avec ARGENT RÉEL!**

**Étapes:**
1. Créer compte Binance: https://www.binance.com
2. Activer 2FA (sécurité)
3. Aller dans Account → API Management
4. Créer clé API
5. **IMPORTANT**: Activer seulement "Enable Reading" et "Enable Spot Trading", PAS de withdrawals!

**Ajouter à .env:**
```bash
BINANCE_API_KEY=your-binance-api-key
BINANCE_API_SECRET=your-binance-secret
```

---

## Premier Lancement

### 1. Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Devrait afficher:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

**Devrait afficher:**
```
  VITE v5.0.0  ready in 500 ms
  ➜  Local:   http://localhost:5173/
```

### 3. Ouvrir Dashboard

1. Ouvrir navigateur
2. Aller sur http://localhost:5173/
3. Vous devriez voir le Dashboard Trading AI

### 4. Démarrer Trading

1. Cliquer sur "Start Trading"
2. Configurer:
   - Capital initial: $10,000 (paper money)
   - Mode: Paper Trading
   - Symbols: BTC/USDT, ETH/USDT
3. Cliquer "Start"

**L'agent devrait commencer à:**
- Monitorer les marchés
- Afficher activité Grok dans le feed
- Exécuter des trades automatiquement

---

## Vérification Installation

### Checklist Backend

```bash
# 1. Backend tourne
curl http://localhost:8000/api/health
# ✅ Devrait retourner: {"status": "healthy"}

# 2. Database connectée
curl http://localhost:8000/api/portfolio/current
# ✅ Devrait retourner portfolio initial

# 3. WebSocket fonctionne
# Ouvrir frontend et vérifier Activity Feed updates

# 4. Grok API configurée
curl http://localhost:8000/api/trading/status
# ✅ Devrait retourner status agent
```

### Checklist Frontend

- [ ] Dashboard s'affiche correctement
- [ ] Métriques (Portfolio, Win Rate, etc.) visibles
- [ ] Graphique Chart.js s'affiche
- [ ] Activity Feed vide au début
- [ ] Boutons Start/Stop fonctionnels
- [ ] Pas d'erreurs dans Console navigateur (F12)

### Checklist Database

```bash
# PostgreSQL
sudo -u postgres psql trading_ai_db -c "SELECT COUNT(*) FROM trades;"

# SQLite
sqlite3 trading_ai.db "SELECT COUNT(*) FROM trades;"

# ✅ Devrait retourner: 0 (aucun trade au début)
```

---

## Troubleshooting

### Problème: "ModuleNotFoundError" Python

**Symptôme:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Vérifier que venv est activé
which python  # Devrait montrer chemin venv

# Réinstaller dépendances
pip install -r requirements.txt
```

### Problème: "Connection to database failed"

**Symptôme:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution PostgreSQL:**
```bash
# Vérifier que PostgreSQL tourne
sudo systemctl status postgresql

# Démarrer si nécessaire
sudo systemctl start postgresql

# Vérifier connection string dans .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

**Solution SQLite:**
```bash
# Vérifier chemin dans .env
DATABASE_URL=sqlite:///./trading_ai.db

# S'assurer que dossier existe
ls -la trading_ai.db
```

### Problème: "CORS Error" Frontend

**Symptôme:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
Vérifier dans `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Redémarrer backend après modification.

### Problème: "Port 8000 already in use"

**Symptôme:**
```
ERROR:    [Errno 48] Address already in use
```

**Solution:**
```bash
# Trouver processus utilisant port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Tuer processus
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Ou utiliser port différent
uvicorn main:app --port 8001
```

### Problème: "Grok API Key Invalid"

**Symptôme:**
```
401 Unauthorized: Invalid API key
```

**Solution:**
```bash
# Vérifier clé API dans .env
echo $GROK_API_KEY

# Tester manuellement
curl https://api.x.ai/v1/models \
  -H "Authorization: Bearer $GROK_API_KEY"

# Si erreur, régénérer clé sur https://x.ai/api
```

### Problème: "npm install fails"

**Symptôme:**
```
npm ERR! code ERESOLVE
```

**Solution:**
```bash
# Nettoyer cache npm
npm cache clean --force

# Supprimer node_modules et package-lock.json
rm -rf node_modules package-lock.json

# Réinstaller
npm install

# Si problème persiste, utiliser --legacy-peer-deps
npm install --legacy-peer-deps
```

### Problème: Frontend ne se connecte pas au Backend

**Symptôme:**
Activity Feed reste vide, aucune mise à jour.

**Solution:**
```bash
# 1. Vérifier que backend tourne
curl http://localhost:8000/api/health

# 2. Vérifier WebSocket URL dans frontend/.env.development
VITE_WS_URL=ws://localhost:8000/ws

# 3. Tester WebSocket manuellement (navigateur console)
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);

# 4. Vérifier logs backend pour erreurs WebSocket
```

### Problème: Alembic migrations fail

**Symptôme:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
```bash
# Vérifier version actuelle
alembic current

# Réinitialiser migrations (⚠️ PERD DONNÉES!)
alembic downgrade base
alembic upgrade head

# Ou créer nouvelle migration
alembic revision --autogenerate -m "Fix schema"
alembic upgrade head
```

---

## Prochaines Étapes

Après installation réussie:

1. **Tester système complet:**
   - Lancer trading avec 1-2 symboles
   - Attendre 5 trades pour voir auto-réflexion
   - Vérifier graphiques et métriques

2. **Configurer surveillance:**
   - Activer Twitter API pour sentiment (optionnel)
   - Activer Google Search pour news (optionnel)
   - Ajuster paramètres risk management selon préférences

3. **Lire documentation:**
   - [API.md](API.md) - Comprendre endpoints disponibles
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture détaillée
   - [DEVELOPMENT.md](DEVELOPMENT.md) - Contribuer au projet

4. **Préparer déploiement:**
   - Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour déployer sur VPS

---

**Installation créée avec ❤️ et Claude Code**
