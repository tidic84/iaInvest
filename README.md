# Trading IA Auto-Apprenant 🤖📈

Système de trading autonome intelligent qui apprend de ses erreurs et améliore continuellement ses performances grâce à l'auto-réflexion.

## 🎯 Caractéristiques Principales

- **Trading Autonome**: L'IA (Grok) trade sans intervention humaine sur marchés crypto et actions
- **Auto-Apprentissage**: Système d'auto-critique après chaque 5 trades
- **Amélioration Continue**: Ajustement automatique de la stratégie
- **Transparence Totale**: Visualisation en temps réel de tous les raisonnements de l'IA
- **Recherches Temps Réel**: Utilisation de Google Search et Twitter/X pour décisions éclairées

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React + TypeScript)          │
│  - Dashboard temps réel                 │
│  - Graphiques Chart.js                  │
│  - Stream activité Grok                 │
└─────────────┬───────────────────────────┘
              │ REST API + WebSocket
┌─────────────▼───────────────────────────┐
│  Backend (Python + FastAPI)             │
│  - Agent Auto-Réflexif                  │
│  - Grok AI (xAI)                        │
│  - Market Data (yfinance, ccxt)         │
│  - WebSocket Server                     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  PostgreSQL / SQLite                    │
│  - Trades, Reflections, Rules           │
└─────────────────────────────────────────┘
```

## 📋 Stack Technique

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **IA**: Grok API (xAI) avec function calling
- **Database**: PostgreSQL ou SQLite
- **Market Data**: yfinance (actions), ccxt (crypto)
- **WebSocket**: python-socketio
- **Async**: asyncio, uvicorn

### Frontend
- **Framework**: React 18+ avec TypeScript
- **Build**: Vite
- **Styling**: TailwindCSS
- **Charts**: Chart.js
- **State**: React Hooks
- **API**: Axios + WebSocket client

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (ou SQLite pour développement)
- Clés API: Grok (xAI), Twitter/X, Google Search

### Installation Locale

```bash
# Cloner le repo
git clone <your-repo-url>
cd trading-ai-project

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Créer .env avec vos clés API
cp .env.example .env
# Éditer .env avec vos clés

# Initialiser database
alembic upgrade head

# Lancer backend
uvicorn main:app --reload

# Frontend (nouveau terminal)
cd ../frontend
npm install
npm run dev
```

### Déploiement VPS

Voir **[DEPLOYMENT.md](DEPLOYMENT.md)** pour instructions détaillées de déploiement sur VPS.

## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Guide d'installation détaillé
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration et variables d'environnement
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Déploiement sur VPS (Ubuntu, Docker, etc.)
- **[API.md](API.md)** - Documentation API REST et WebSocket
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture technique détaillée
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guide de développement

## 🔑 Clés API Requises

| Service | Utilisation | Coût | Obtention |
|---------|-------------|------|-----------|
| **Grok (xAI)** | IA trading & auto-réflexion | $4-6/semaine | https://x.ai/api |
| **Twitter/X** | Sentiment analysis | Gratuit (limites) | https://developer.twitter.com |
| **Google Search** | Recherches internet | Gratuit (100/jour) | https://developers.google.com/custom-search |

## 💰 Coûts Estimés

**Mode Paper Trading:**
- Grok API: $4-6/semaine (~$20-25/mois)
- Autres APIs: Gratuit
- VPS: $10-20/mois (2 vCPU, 4GB RAM)
- **TOTAL: ~$30-45/mois**

## ⚠️ Sécurité

- ✅ Mode **Paper Trading** par défaut (simulation sans argent réel)
- ✅ Stop-Loss et Take-Profit automatiques
- ✅ Limites strictes: max 3 positions, -20% drawdown
- ✅ Emergency stop si perte > 10% en 1 jour
- ✅ Toutes les clés API dans `.env` (gitignored)

## 📊 Fonctionnalités

### Trading Autonome
- Recherches internet temps réel (Google)
- Analyse sentiment Twitter/X
- Indicateurs techniques (RSI, MACD, Bollinger)
- Décisions de trading automatiques

### Auto-Réflexion
- Analyse après chaque 5 trades
- Identification des erreurs (overtrading, vitesse, sentiment)
- Extraction des succès
- Ajustement automatique de la stratégie
- Nouvelles règles apprises

### Dashboard Temps Réel
- Stream d'activité Grok en direct
- Graphiques performance (Chart.js)
- Positions ouvertes avec P&L live
- Cartes de réflexion détaillées
- Contrôles manuels (force reflection, manual trade)

## 🧪 Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Tests end-to-end
npm run test:e2e
```

## 📈 Métriques de Succès

- Win rate > 55% (après 50+ trades)
- Max drawdown < 15%
- ROI > 0% sur 1 mois
- Trades/jour: 3-7
- Nouvelles règles: 2-3 par réflexion
- Amélioration win rate: +5-10% après 3 cycles

## 🤝 Contribution

Ce projet est à but éducatif. Contributions bienvenues!

## ⚖️ Disclaimer

**IMPORTANT**: Ce système est à but éducatif et expérimental.
- ❌ Pas de garantie de profits
- ❌ Trading = risque de pertes financières
- ✅ Commencer en mode Paper Trading
- ✅ L'utilisateur assume tous les risques

## 📝 License

MIT License - Voir LICENSE file

## 🆘 Support

- Issues: GitHub Issues
- Documentation: Voir dossier `/docs`
- Email: [votre-email]

---

**Développé avec ❤️ et Claude Code**
