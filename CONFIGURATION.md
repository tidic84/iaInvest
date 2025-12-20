# Guide de Configuration 🔧

Ce document détaille toutes les variables d'environnement et options de configuration du système.

## 📋 Table des Matières

1. [Variables d'Environnement Backend](#variables-denvironnement-backend)
2. [Variables d'Environnement Frontend](#variables-denvironnement-frontend)
3. [Configuration Base de Données](#configuration-base-de-données)
4. [Clés API](#clés-api)
5. [Configuration Trading](#configuration-trading)
6. [Configuration Sécurité](#configuration-sécurité)
7. [Configuration Logging](#configuration-logging)

---

## Variables d'Environnement Backend

### Fichier `.env` Backend

Localisation: `backend/.env`

```bash
# ============================================
# CONFIGURATION GÉNÉRALE
# ============================================

# Environnement (development, staging, production)
ENVIRONMENT=production

# Mode debug (True pour dev, False pour prod)
DEBUG=False

# Clé secrète (générer avec: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire-ici

# ============================================
# BASE DE DONNÉES
# ============================================

# PostgreSQL (Production)
DATABASE_URL=postgresql://trading_user:password@localhost:5432/trading_ai_db

# SQLite (Développement - plus simple)
# DATABASE_URL=sqlite:///./trading_ai.db

# Pool de connexions
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# ============================================
# CLÉS API
# ============================================

# Grok (xAI) - https://x.ai/api
GROK_API_KEY=xai-VOTRE-CLE-GROK-ICI
GROK_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-beta

# Twitter/X API - https://developer.twitter.com
TWITTER_API_KEY=votre-api-key
TWITTER_API_SECRET=votre-api-secret
TWITTER_ACCESS_TOKEN=votre-access-token
TWITTER_ACCESS_SECRET=votre-access-secret
TWITTER_BEARER_TOKEN=votre-bearer-token

# Google Search API - https://developers.google.com/custom-search
GOOGLE_SEARCH_API_KEY=votre-google-api-key
GOOGLE_SEARCH_ENGINE_ID=votre-search-engine-id

# Binance API (Optionnel - seulement pour trading crypto LIVE)
BINANCE_API_KEY=votre-binance-key
BINANCE_API_SECRET=votre-binance-secret

# ============================================
# CONFIGURATION TRADING
# ============================================

# Mode de trading (paper, live)
# ATTENTION: Commencer TOUJOURS par "paper" !
TRADING_MODE=paper

# Capital initial (USD)
INITIAL_CAPITAL=10000

# Actifs surveillés (séparés par virgule)
WATCHED_SYMBOLS=BTC/USDT,ETH/USDT,AAPL,TSLA,NVDA

# Limites de positions
MAX_POSITIONS=3
MAX_POSITION_SIZE_PCT=20

# Risk Management
STOP_LOSS_DEFAULT=5
TAKE_PROFIT_DEFAULT=10
MAX_DRAWDOWN=20
MAX_DAILY_LOSS_PCT=10

# Trading Frequency
MAX_TRADES_PER_DAY=5
MIN_INTERVAL_BETWEEN_TRADES=3600  # secondes (1h)

# Auto-réflexion
REFLECTION_INTERVAL=5  # Nombre de trades avant auto-réflexion
REFLECTION_ENABLED=True

# ============================================
# CONFIGURATION SERVEUR
# ============================================

# Host & Port
HOST=0.0.0.0
PORT=8000

# Workers (production)
WORKERS=4

# Timeout
TIMEOUT=120

# ============================================
# CORS (Cross-Origin Resource Sharing)
# ============================================

# Origins autorisées (séparées par virgule)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com,https://www.yourdomain.com

# Méthodes autorisées
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS

# Headers autorisés
CORS_HEADERS=*

# ============================================
# CACHE & OPTIMISATION
# ============================================

# Redis (optionnel - pour cache)
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=False

# Cache TTL (secondes)
SENTIMENT_CACHE_TTL=3600  # 1h
MARKET_DATA_CACHE_TTL=60  # 1min
NEWS_CACHE_TTL=1800  # 30min

# ============================================
# RATE LIMITING
# ============================================

# Grok API
GROK_MAX_CALLS_PER_TRADE=10
GROK_COOLDOWN_SECONDS=180  # 3 min entre checks

# Twitter API
TWITTER_MAX_REQUESTS_PER_15MIN=50

# Market Data
MARKET_CHECK_INTERVAL=180  # 3 min

# ============================================
# LOGGING
# ============================================

# Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Fichier de log
LOG_FILE=/var/log/trading-ai/backend.log

# Rotation des logs
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Log JSON format (pour parsing facile)
LOG_JSON_FORMAT=False

# ============================================
# MONITORING & ALERTES
# ============================================

# Email notifications (optionnel)
SMTP_ENABLED=False
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password
ALERT_EMAIL=votre-email@gmail.com

# Alertes
ALERT_ON_TRADE=False
ALERT_ON_REFLECTION=True
ALERT_ON_ERROR=True
ALERT_ON_LOSS_THRESHOLD=-5  # % loss

# ============================================
# SÉCURITÉ
# ============================================

# JWT Token
JWT_SECRET_KEY=autre-cle-secrete-pour-jwt
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Rate Limiting
API_RATE_LIMIT=100  # requêtes par minute

# ============================================
# BACKUP
# ============================================

# Backup automatique
AUTO_BACKUP_ENABLED=True
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=7
BACKUP_PATH=/home/trading/backups
```

---

## Variables d'Environnement Frontend

### Fichier `.env.production` Frontend

Localisation: `frontend/.env.production`

```bash
# Backend API URL
VITE_API_URL=https://api.yourdomain.com

# WebSocket URL
VITE_WS_URL=wss://api.yourdomain.com/ws

# Mode (development, production)
VITE_MODE=production

# Analytics (optionnel)
VITE_GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X

# Sentry (Error tracking - optionnel)
VITE_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# Feature Flags
VITE_ENABLE_MANUAL_TRADE=true
VITE_ENABLE_FORCE_REFLECTION=true
VITE_ENABLE_EXPORT=true

# Refresh Rates (milliseconds)
VITE_PORTFOLIO_REFRESH_MS=5000  # 5s
VITE_CHART_REFRESH_MS=10000     # 10s

# UI Settings
VITE_DEFAULT_THEME=dark
VITE_CHART_ANIMATION=true
```

### Fichier `.env.development` Frontend

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_MODE=development
VITE_ENABLE_MANUAL_TRADE=true
VITE_ENABLE_FORCE_REFLECTION=true
VITE_ENABLE_EXPORT=true
```

---

## Configuration Base de Données

### PostgreSQL (Production)

```bash
# Connection String Format
postgresql://[user]:[password]@[host]:[port]/[database]

# Exemple
DATABASE_URL=postgresql://trading_user:MySecureP@ss123@localhost:5432/trading_ai_db
```

**Configuration PostgreSQL** (`/etc/postgresql/15/main/postgresql.conf`):
```conf
# Connexions
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Write-Ahead Log
wal_buffers = 16MB
checkpoint_completion_target = 0.9
```

### SQLite (Développement)

```bash
# Fichier local
DATABASE_URL=sqlite:///./trading_ai.db

# Ou chemin absolu
DATABASE_URL=sqlite:////home/trading/trading-ai/backend/trading_ai.db
```

---

## Clés API

### 1. Grok (xAI)

**Obtention:** https://x.ai/api

**Configuration:**
```bash
GROK_API_KEY=xai-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Test:**
```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GROK_API_KEY" \
  -d '{
    "model": "grok-beta",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### 2. Twitter/X API

**Obtention:** https://developer.twitter.com/en/portal/dashboard

**Niveau requis:** Essential (gratuit) ou Elevated

**Configuration:**
```bash
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```

**Test:**
```bash
curl "https://api.twitter.com/2/tweets/search/recent?query=bitcoin" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

### 3. Google Custom Search API

**Obtention:**
1. https://developers.google.com/custom-search/v1/introduction
2. https://programmablesearchengine.google.com/

**Limites:** 100 requêtes/jour (gratuit)

**Configuration:**
```bash
GOOGLE_SEARCH_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SEARCH_ENGINE_ID=xxxxxxxxxxxxxxxxx
```

**Test:**
```bash
curl "https://www.googleapis.com/customsearch/v1?key=$GOOGLE_SEARCH_API_KEY&cx=$GOOGLE_SEARCH_ENGINE_ID&q=bitcoin+news"
```

### 4. Binance API (Optionnel)

**Obtention:** https://www.binance.com/en/my/settings/api-management

**⚠️ Seulement pour trading crypto LIVE!**

**Configuration:**
```bash
BINANCE_API_KEY=your-binance-api-key
BINANCE_API_SECRET=your-binance-secret
```

**Permissions requises:**
- ✅ Enable Reading (obligatoire)
- ✅ Enable Spot & Margin Trading (si trading live)
- ❌ Enable Withdrawals (NON - sécurité)

---

## Configuration Trading

### Modes de Trading

#### Paper Trading (Recommandé au début)
```bash
TRADING_MODE=paper
INITIAL_CAPITAL=10000
```
- Simulation complète
- Pas d'argent réel
- Prix du marché réels
- Parfait pour tester stratégies

#### Live Trading (Avancé)
```bash
TRADING_MODE=live
INITIAL_CAPITAL=1000  # Commencer petit!
```
- ⚠️ ARGENT RÉEL!
- Nécessite clés API exchange (Binance)
- Commissions réelles
- Risque de perte

### Paramètres Risk Management

```bash
# Position sizing
MAX_POSITION_SIZE_PCT=20      # Max 20% du capital par position
MAX_POSITIONS=3                # Max 3 positions simultanées

# Stop-loss & Take-profit
STOP_LOSS_DEFAULT=5           # -5% stop-loss
TAKE_PROFIT_DEFAULT=10        # +10% take-profit

# Drawdown protection
MAX_DRAWDOWN=20               # Stop si -20% depuis ATH
MAX_DAILY_LOSS_PCT=10         # Stop si -10% en 1 jour

# Trading frequency
MAX_TRADES_PER_DAY=5
MIN_INTERVAL_BETWEEN_TRADES=3600  # 1h minimum entre trades
```

### Stratégie Initiale

```bash
# Poids des facteurs de décision
SENTIMENT_WEIGHT=0.3          # 30% sentiment
TECHNICAL_WEIGHT=0.7          # 70% technique

# Seuils RSI
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70

# Seuils sentiment
MIN_SENTIMENT_FOR_BUY=0.65    # Min 0.65 pour acheter
MAX_SENTIMENT_FOR_SELL=0.35   # Max 0.35 pour vendre
```

---

## Configuration Sécurité

### JWT Tokens

```bash
# Générer clé secrète
python -c "import secrets; print(secrets.token_hex(32))"

JWT_SECRET_KEY=<output-de-la-commande>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### CORS

```bash
# Production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Développement (accepte localhost)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Rate Limiting

```bash
# API publique
API_RATE_LIMIT=100            # 100 req/min

# APIs externes
GROK_MAX_CALLS_PER_TRADE=10
TWITTER_MAX_REQUESTS_PER_15MIN=50
```

---

## Configuration Logging

### Niveaux de Log

```bash
# DEBUG: Tout (très verbeux)
LOG_LEVEL=DEBUG

# INFO: Informations importantes (recommandé dev)
LOG_LEVEL=INFO

# WARNING: Warnings + erreurs (recommandé staging)
LOG_LEVEL=WARNING

# ERROR: Seulement erreurs (recommandé prod)
LOG_LEVEL=ERROR
```

### Rotation des Logs

```bash
# Fichier de log
LOG_FILE=/var/log/trading-ai/backend.log

# Taille max avant rotation
LOG_MAX_BYTES=10485760        # 10 MB

# Nombre de fichiers gardés
LOG_BACKUP_COUNT=5            # Garder 5 fichiers
```

### Format de Log

**Standard (lisible):**
```bash
LOG_JSON_FORMAT=False
```
Output:
```
2024-12-20 15:30:00 - INFO - Trade executed: BUY BTC/USDT $2000
```

**JSON (parsing facile):**
```bash
LOG_JSON_FORMAT=True
```
Output:
```json
{"timestamp": "2024-12-20T15:30:00", "level": "INFO", "message": "Trade executed", "symbol": "BTC/USDT", "amount": 2000}
```

---

## Validation de Configuration

### Script de Validation

Créer `backend/validate_config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = [
    'DATABASE_URL',
    'GROK_API_KEY',
    'SECRET_KEY',
    'TRADING_MODE',
]

OPTIONAL_VARS = [
    'TWITTER_API_KEY',
    'GOOGLE_SEARCH_API_KEY',
    'REDIS_URL',
]

def validate_config():
    errors = []
    warnings = []

    # Check required
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            errors.append(f"❌ {var} is required but not set")

    # Check optional
    for var in OPTIONAL_VARS:
        if not os.getenv(var):
            warnings.append(f"⚠️  {var} is optional but not set")

    # Validations spécifiques
    if os.getenv('TRADING_MODE') not in ['paper', 'live']:
        errors.append("❌ TRADING_MODE must be 'paper' or 'live'")

    if os.getenv('TRADING_MODE') == 'live' and not os.getenv('BINANCE_API_KEY'):
        errors.append("❌ BINANCE_API_KEY required for live trading")

    # Results
    if errors:
        print("\n".join(errors))
        return False

    if warnings:
        print("\n".join(warnings))

    print("✅ Configuration is valid!")
    return True

if __name__ == "__main__":
    validate_config()
```

**Utilisation:**
```bash
cd backend
python validate_config.py
```

---

## Exemples de Configuration

### Développement Local

```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./trading_ai.db
TRADING_MODE=paper
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000
```

### Staging

```bash
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://user:pass@staging-db:5432/trading_ai
TRADING_MODE=paper
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.yourdomain.com
```

### Production

```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/trading_ai
TRADING_MODE=paper  # Ou live après validation
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
WORKERS=4
AUTO_BACKUP_ENABLED=True
```

---

## Troubleshooting

### Problèmes Courants

**1. Database connection failed**
```bash
# Vérifier connection string
echo $DATABASE_URL

# Tester PostgreSQL
psql $DATABASE_URL -c "SELECT 1;"
```

**2. CORS errors**
```bash
# Vérifier origins
echo $CORS_ORIGINS

# Doit inclure URL frontend exact (avec/sans www, http/https)
```

**3. API keys invalid**
```bash
# Tester Grok
curl https://api.x.ai/v1/models -H "Authorization: Bearer $GROK_API_KEY"

# Tester Twitter
curl "https://api.twitter.com/2/tweets/search/recent?query=test" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

---

**Configuration créée avec ❤️ et Claude Code**
