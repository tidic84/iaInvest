# Architecture du Trader Autonome Grok

## Vue d'ensemble

Transformer Grok en un trader professionnel autonome qui :
- ✅ Définit et maintient sa propre stratégie
- ✅ Fait des recherches actives sur le web et X.com
- ✅ Découvre de nouvelles opportunités
- ✅ Reste à l'affût des actualités
- ✅ Agit selon sa stratégie avec discipline
- ✅ Apprend et s'adapte en continu

---

## 6 Cycles Principaux

### 1. CYCLE DE STRATÉGIE
**Fréquence** : Au démarrage + après réflexions majeures

**Objectif** : Définir et maintenir une stratégie de trading cohérente

**Actions** :
- Grok analyse le capital disponible, le profil de risque
- Définit son style : day trading, swing trading, growth, value, momentum
- Établit critères d'entrée (indicateurs, catalyseurs, patterns)
- Établit critères de sortie (targets, stop-loss, trailing stops)
- Définit règles de risk management (max position size, drawdown limits)
- Stocke la stratégie en base de données

**Outils Grok utilisés** :
- `code_execution()` : Backtesting statistiques
- Raisonnement interne

**Exemple de stratégie** :
```json
{
  "style": "momentum_growth",
  "holding_period": "3-10 days",
  "entry_criteria": {
    "catalysts": ["earnings_beat", "product_launch", "viral_trend"],
    "technical": ["RSI < 70", "Volume > avg_20d * 1.5"],
    "sentiment": ["x_mentions_growing", "positive_sentiment > 0.6"]
  },
  "exit_criteria": {
    "take_profit": "15-25%",
    "stop_loss": "7%",
    "trailing_stop": "5% after +10% gain"
  },
  "risk_management": {
    "max_position_size": "20%",
    "max_positions": 5,
    "max_daily_loss": "5%"
  }
}
```

---

### 2. CYCLE DE DÉCOUVERTE (Discovery)
**Fréquence** : Toutes les heures (configurable)

**Objectif** : Scanner le marché pour identifier de nouvelles opportunités

**Actions** :
1. **Recherche Web** via `web_search()` :
   - "Latest stock market news today"
   - "Companies with earnings beat this week"
   - "Upcoming IPOs and SPACs"
   - "Merger and acquisition announcements"
   - "FDA approvals biotech"
   - "Tech product launches"

2. **Recherche X.com** via `x_search()` :
   - Trending tickers ($AAPL, $TSLA, etc.)
   - Viral financial threads
   - Influenceurs finance (user_search)
   - Hashtags : #stockmarket #trading #crypto

3. **Analyse des résultats** :
   - Extraire symboles mentionnés
   - Évaluer pertinence selon stratégie
   - Scorer chaque opportunité
   - Ajouter à la watchlist

**Output** :
- Watchlist dynamique avec scores et raisons

**Exemple** :
```
NVDA : Score 8.5/10
Raison : Annonce nouveau GPU + mentions massives sur X + volume anormal
Source : web_search (TechCrunch), x_search (45k mentions en 24h)

COIN : Score 6.2/10
Raison : Bitcoin rally + earnings dans 2 jours
Source : web_search (Bloomberg), x_search (sentiment positif 0.72)
```

---

### 3. CYCLE D'ANALYSE
**Fréquence** : Toutes les 30 minutes

**Objectif** : Analyser en profondeur les symboles sur la watchlist

**Actions pour chaque symbole** :
1. **Recherche contextuelle** :
   - `web_search()` : "SYMBOL recent news analysis"
   - `x_search()` : $SYMBOL sentiment et discussions

2. **Analyse technique** :
   - Récupérer prix et indicateurs (RSI, MACD, Volume, etc.)
   - Identifier patterns (breakout, support/resistance)

3. **Analyse fondamentale** :
   - Context des actualités
   - Catalyseurs à venir
   - Sentiment général

4. **Vérification stratégie** :
   - Est-ce conforme à ma stratégie ?
   - Risk/reward favorable ?
   - Timing approprié ?

5. **Décision** :
   - BUY (avec taille position, stop-loss, take-profit)
   - HOLD (continuer surveillance)
   - REMOVE (retirer de watchlist)

**Output** :
- Décisions de trading avec justifications détaillées

---

### 4. CYCLE DE TRADING (Execution)
**Fréquence** : À la demande (après décision BUY)

**Objectif** : Exécuter les trades avec discipline

**Actions** :
1. **Vérifications pre-trade** :
   - Capital disponible suffisant ?
   - Nombre max positions respecté ?
   - Exposition totale acceptable ?
   - Pas de corrélation excessive avec positions existantes ?

2. **Calcul position sizing** :
   - Basé sur stratégie et capital
   - Ajusté selon niveau de confiance
   - Respect du risk management

3. **Exécution** :
   - Créer trade en base
   - Mettre à jour portfolio
   - Logger détails complets

4. **Configuration exits** :
   - Stop-loss automatique
   - Take-profit targets
   - Trailing stop si applicable

**Output** :
- Trade exécuté avec tous les paramètres enregistrés

---

### 5. CYCLE DE VEILLE (Monitoring)
**Fréquence** : Toutes les 15 minutes

**Objectif** : Surveiller positions ouvertes et réagir aux événements

**Actions pour chaque position ouverte** :
1. **Vérification prix** :
   - P&L actuel
   - Distance stop-loss / take-profit
   - Activation trailing stop si applicable

2. **Veille actualités** :
   - `web_search()` : "SYMBOL breaking news" (dernière heure)
   - Détection événements majeurs (earnings surprise, scandal, etc.)

3. **Veille sentiment** :
   - `x_search()` : $SYMBOL (dernière heure)
   - Changements soudains de sentiment
   - Spike de volume de mentions

4. **Décision ajustement** :
   - **EXIT anticipé** : si breaking news négative ou stratégie invalidée
   - **Ajuster stop-loss** : si trailing stop activé
   - **Prendre profits partiels** : si target intermédiaire atteint
   - **HOLD** : si tout va bien

**Output** :
- Alertes et ajustements de positions

**Exemple** :
```
⚠️ ALERTE NVDA
Breaking news: CEO vend 50M$ d'actions
Sentiment X.com: 0.72 → 0.41 en 2h
Décision: EXIT partiel (50% position) + trailing stop serré
```

---

### 6. CYCLE DE RÉFLEXION
**Fréquence** : Après chaque N trades fermés (ex: 10)

**Objectif** : Apprendre et améliorer la stratégie

**Actions** :
1. **Analyse performance** :
   - Win rate, profit factor, max drawdown
   - Performance par style de trade
   - Trades gagnants vs perdants

2. **Identification patterns** :
   - Qu'est-ce qui a bien fonctionné ?
   - Quelles erreurs répétées ?
   - Catalyseurs les plus profitables ?

3. **Validation stratégie** :
   - La stratégie est-elle suivie ?
   - Faut-il l'ajuster ?
   - Nouvelles règles à ajouter ?

4. **Apprentissage** :
   - Créer nouvelles règles apprises
   - Ajuster paramètres stratégie
   - Améliorer critères de sélection

**Output** :
- Rapport de réflexion
- Stratégie mise à jour
- Nouvelles règles

---

## Nouveaux Modèles de Base de Données

### 1. TradingStrategy
```python
{
  "id": int,
  "version": int,  # Versioning des stratégies
  "created_at": datetime,
  "is_active": bool,
  "style": str,  # "momentum", "growth", "value", etc.
  "description": str,
  "entry_criteria": json,
  "exit_criteria": json,
  "risk_management": json,
  "parameters": json,  # Paramètres supplémentaires
  "performance_metrics": json  # Métriques de performance
}
```

### 2. Watchlist
```python
{
  "id": int,
  "symbol": str,
  "added_at": datetime,
  "score": float,  # 0-10
  "reason": str,
  "sources": json,  # web_search et x_search results
  "priority": str,  # "high", "medium", "low"
  "status": str,  # "watching", "analyzing", "traded", "removed"
  "last_analyzed": datetime,
  "metadata": json  # Données supplémentaires
}
```

### 3. MarketEvent
```python
{
  "id": int,
  "timestamp": datetime,
  "event_type": str,  # "earnings", "news", "sentiment_change", etc.
  "symbol": str,
  "severity": str,  # "low", "medium", "high", "critical"
  "description": str,
  "source": str,  # "web_search", "x_search"
  "impact_assessment": str,
  "action_taken": str,  # "none", "exit", "adjust_stop", etc.
  "related_trade_id": int,
  "metadata": json
}
```

### 4. StrategyAdjustment
```python
{
  "id": int,
  "timestamp": datetime,
  "strategy_id": int,
  "adjustment_type": str,  # "parameter_change", "new_rule", "criteria_update"
  "reason": str,
  "changes": json,  # Détails des changements
  "performance_before": json,
  "performance_after": json,  # Rempli plus tard
  "created_by": str  # "reflection", "manual", "auto"
}
```

---

## Implémentation Technique

### Structure des fichiers

```
backend/app/
├── models/
│   ├── trading_strategy.py      # NEW
│   ├── watchlist.py              # NEW
│   ├── market_event.py           # NEW
│   ├── strategy_adjustment.py   # NEW
│   ├── trade.py                 # UPDATED
│   └── ...
├── services/
│   ├── grok_service.py           # REFONTE COMPLÈTE
│   ├── trading_agent.py          # REFONTE COMPLÈTE
│   ├── strategy_service.py       # NEW
│   ├── discovery_service.py      # NEW
│   ├── monitoring_service.py     # NEW
│   └── ...
```

### grok_service.py - Nouvelles méthodes

```python
class GrokService:
    # CYCLE 1: Stratégie
    def create_trading_strategy(self, capital, risk_profile)

    # CYCLE 2: Découverte
    def discover_opportunities(self)
    def analyze_web_news(self)
    def analyze_x_trends(self)
    def score_opportunity(self, symbol, context)

    # CYCLE 3: Analyse
    def deep_analyze_symbol(self, symbol, watchlist_context)
    def check_strategy_alignment(self, opportunity, strategy)

    # CYCLE 5: Veille
    def monitor_position(self, trade, current_price)
    def detect_breaking_news(self, symbol)
    def assess_sentiment_change(self, symbol)

    # CYCLE 6: Réflexion (existant mais amélioré)
    def reflect_on_strategy(self, trades, current_strategy)
```

### Utilisation des Outils Agentiques

**Important** : Avec xai-sdk >= 1.3.1, on utilise les outils de manière agentique :

```python
from xai_sdk import Client
from xai_sdk.tools import web_search, x_search, code_execution

chat = client.chat.create(
    model="grok-2-1212",
    tools=[
        web_search(),
        x_search(),
        code_execution()
    ]
)

# Grok décide AUTOMATIQUEMENT quand et comment utiliser les outils
chat.append(user(
    "Trouve les 5 actions les plus prometteuses basées sur les actualités "
    "des dernières 24h et le sentiment sur X. Cherche des catalyseurs comme "
    "earnings beats, lancements produits, ou tendances virales."
))

# Grok va :
# 1. web_search() pour actualités
# 2. x_search() pour tendances
# 3. code_execution() pour analyser les données
# 4. Retourner une réponse structurée
```

---

## Configuration

### Nouveaux paramètres .env

```bash
# Grok Agentic Mode
GROK_MODEL=grok-2-1212
GROK_AGENTIC_MODE=true

# Cycles timing (en secondes)
DISCOVERY_INTERVAL=3600       # 1h
ANALYSIS_INTERVAL=1800        # 30min
MONITORING_INTERVAL=900       # 15min
REFLECTION_TRADES_THRESHOLD=10

# Stratégie
AUTO_STRATEGY_CREATION=true
STRATEGY_RISK_PROFILE=moderate  # conservative, moderate, aggressive

# Watchlist
MAX_WATCHLIST_SIZE=20
MIN_OPPORTUNITY_SCORE=6.0
AUTO_REMOVE_LOW_PRIORITY_DAYS=7
```

---

## Workflow de Démarrage

1. **Initialisation** :
   - Grok crée sa stratégie initiale
   - L'utilisateur peut la valider/modifier
   - Stratégie enregistrée en base

2. **Premier cycle découverte** :
   - Grok fait des recherches
   - Construit watchlist initiale

3. **Cycles continus** :
   - Découverte (toutes les heures)
   - Analyse (toutes les 30 min)
   - Monitoring (toutes les 15 min)
   - Trading (à la demande)
   - Réflexion (après N trades)

---

## Avantages de cette Architecture

✅ **Autonomie** : Grok est un vrai trader autonome
✅ **Discipline** : Respecte sa stratégie
✅ **Réactivité** : Répond aux actualités en temps réel
✅ **Apprentissage** : S'améliore en continu
✅ **Transparence** : Toutes les décisions sont loggées et justifiées
✅ **Contrôle** : L'utilisateur peut superviser et ajuster

---

## Prochaines Étapes

1. ✅ Valider cette architecture
2. Créer les nouveaux modèles de BDD
3. Migrer la base de données
4. Refondre grok_service.py
5. Refondre trading_agent.py
6. Créer les nouveaux services
7. Mettre à jour xai-sdk
8. Tests
9. Déploiement
