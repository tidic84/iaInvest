"""
Grok Service - Interface avec l'API Grok xAI en mode agentique
Utilise les outils web_search, x_search et code_execution
"""
import json
import os
from xai_sdk import Client
from xai_sdk.chat import user, assistant
from xai_sdk.tools import web_search, x_search, code_execution
from app.config import settings
from typing import Dict, List, Any, Optional
from loguru import logger


class GrokService:
    def __init__(self):
        self.client = Client(api_key=settings.XAI_API_KEY)
        self.model = settings.GROK_MODEL
        # Outils agentiques disponibles
        self.agentic_tools = [web_search(), x_search(), code_execution()]

    # ==================== CYCLE 1: STRATÉGIE ====================

    def create_trading_strategy(
        self, capital: float, risk_profile: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Demande à Grok de créer une stratégie de trading complète
        Grok utilise code_execution pour faire des backtests
        """
        prompt = f"""You are an expert trading strategist. Create a comprehensive trading strategy for an autonomous AI trader.

Available Capital: ${capital:,.2f}
Risk Profile: {risk_profile}

Using your code_execution tool, analyze historical market data and create a strategy with:

1. **Trading Style**: Define the primary approach (momentum, growth, value, swing, day trading, etc.)
2. **Entry Criteria**: What signals/conditions trigger a BUY decision
   - Technical indicators (RSI, MACD, Volume, etc.)
   - Fundamental catalysts (earnings, product launches, etc.)
   - Sentiment signals (X mentions, news sentiment)
3. **Exit Criteria**: When to close positions
   - Take profit targets
   - Stop-loss rules
   - Trailing stop configuration
4. **Risk Management**: Position sizing and risk limits
   - Max position size (% of capital)
   - Max number of concurrent positions
   - Max daily loss limit
   - Correlation limits

Return your strategy as a JSON object following this structure:
{{
    "style": "momentum_growth",
    "holding_period": "3-10 days",
    "description": "Brief description of the strategy",
    "entry_criteria": {{
        "catalysts": ["earnings_beat", "product_launch", "viral_trend"],
        "technical": ["RSI < 70", "Volume > avg_20d * 1.5"],
        "sentiment": ["x_mentions_growing", "positive_sentiment > 0.6"]
    }},
    "exit_criteria": {{
        "take_profit": "15-25%",
        "stop_loss": "7%",
        "trailing_stop": "5% after +10% gain"
    }},
    "risk_management": {{
        "max_position_size": 20,
        "max_positions": 5,
        "max_daily_loss": 5
    }},
    "parameters": {{
        "sentiment_weight": 0.4,
        "technical_weight": 0.6
    }}
}}
"""

        try:
            chat = self.client.chat.create(
                model=self.model, messages=[user(prompt)], tools=self.agentic_tools
            )

            response_text = self._get_final_response(chat)
            strategy = self._extract_json(response_text)

            logger.info(f"Stratégie créée par Grok: {strategy.get('style', 'unknown')}")
            return strategy

        except Exception as e:
            logger.error(f"Erreur lors de la création de stratégie: {e}")
            return self._get_default_strategy(capital, risk_profile)

    # ==================== CYCLE 2: DÉCOUVERTE ====================

    def discover_opportunities(self) -> Dict[str, Any]:
        """
        Grok recherche activement des opportunités via web_search et x_search
        Returns dict with 'opportunities' list and 'full_analysis' text
        """
        prompt = """You are an autonomous trading AI on a discovery mission. Use your tools to find promising trading opportunities.

Tasks:
1. Use web_search() to find:
   - Latest stock market news
   - Companies with earnings beats this week
   - Upcoming IPOs and SPACs
   - M&A announcements
   - FDA approvals (biotech/pharma)
   - Major tech product launches

2. Use x_search() to identify:
   - Trending stock tickers ($SYMBOL)
   - Viral financial discussions
   - Sentiment shifts
   - Popular #stockmarket, #trading hashtags

3. Score each opportunity (0-10) based on:
   - News impact and freshness
   - Social media buzz
   - Volume/price action
   - Relevance to momentum/growth trading

Return a JSON array of the TOP 10 opportunities:
[
    {{
        "symbol": "NVDA",
        "score": 8.5,
        "reason": "New GPU announcement + massive X mentions + unusual volume",
        "sources": {{
            "web_news": ["URL1", "URL2"],
            "x_trends": {{"mentions_24h": 45000, "sentiment": 0.78}}
        }},
        "catalysts": ["product_launch", "social_viral"]
    }},
    ...
]
"""

        try:
            chat = self.client.chat.create(
                model=self.model, messages=[user(prompt)], tools=self.agentic_tools
            )

            response_text = self._get_final_response(chat)
            opportunities = self._extract_json(response_text)

            # Assure que c'est une liste
            if isinstance(opportunities, dict):
                opportunities = [opportunities]

            logger.info(f"Découverte terminée: {len(opportunities)} opportunités trouvées")
            return {
                "opportunities": opportunities,
                "full_analysis": response_text
            }

        except Exception as e:
            logger.error(f"Erreur lors de la découverte: {e}")
            return {
                "opportunities": [],
                "full_analysis": f"Error during discovery: {str(e)}"
            }

    # ==================== CYCLE 3: ANALYSE ====================

    def deep_analyze_symbol(
        self, symbol: str, watchlist_context: Dict[str, Any], strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyse approfondie d'un symbole avec recherche web/X + analyse technique
        """
        prompt = f"""You are analyzing {symbol} for a potential trade.

Watchlist Context:
{json.dumps(watchlist_context, indent=2)}

Active Trading Strategy:
{json.dumps(strategy, indent=2)}

Tasks:
1. Use web_search() for "{symbol} recent news analysis stock"
2. Use x_search() for "${symbol}" sentiment and discussions
3. Use code_execution() to analyze technical indicators (fetch price data if needed)

Evaluate:
- Does this align with our strategy criteria?
- Risk/reward ratio
- Timing (is NOW the right time?)

Return decision as JSON:
{{
    "decision": "BUY" | "HOLD" | "REMOVE",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation",
    "alignment_score": 0.0-1.0,  // How well it matches our strategy
    "risk_assessment": "Low" | "Medium" | "High",
    "position_size_pct": 10-20,  // If BUY
    "stop_loss_pct": 3-7,
    "take_profit_pct": 8-15,
    "entry_conditions": "What to wait for before entering"
}}
"""

        try:
            chat = self.client.chat.create(
                model=self.model, messages=[user(prompt)], tools=self.agentic_tools
            )

            response_text = self._get_final_response(chat)
            analysis = self._extract_json(response_text)

            # Add the full response text to the analysis
            analysis["full_analysis"] = response_text

            logger.info(f"Analyse de {symbol}: {analysis.get('decision', 'N/A')}")
            return analysis

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {symbol}: {e}")
            return {
                "decision": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "risk_assessment": "High",
                "full_analysis": f"Error during analysis: {str(e)}"
            }

    # ==================== CYCLE 4: TRADING (utilise l'ancien analyze_market amélioré) ====================

    def analyze_market(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict[str, Any],
        sentiment_data: Optional[Dict] = None,
        learned_rules: List[str] = None,
        strategy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyse de marché pour décision de trading
        Version améliorée avec stratégie
        """
        learned_rules_str = "\n".join(f"- {rule}" for rule in (learned_rules or []))
        strategy_str = json.dumps(strategy, indent=2) if strategy else "No active strategy"

        prompt = f"""You are an expert trading AI. Analyze this market data and decide on trade action.

Symbol: {symbol}
Current Price: ${current_price}

Technical Indicators:
{json.dumps(indicators, indent=2)}

Sentiment Data:
{json.dumps(sentiment_data or {}, indent=2)}

Active Strategy:
{strategy_str}

Learned Rules:
{learned_rules_str if learned_rules_str else "No rules yet"}

Decision required as JSON:
{{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation",
    "risk_assessment": "Low" | "Medium" | "High",
    "position_size_pct": 10-20,
    "stop_loss_pct": 3-7,
    "take_profit_pct": 8-15,
    "strategy_alignment": true/false
}}
"""

        try:
            chat = self.client.chat.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI trading agent. Always respond with valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            response_text = self._get_final_response(chat)
            decision = self._extract_json(response_text)
            return decision

        except Exception as e:
            logger.error(f"Error calling Grok API: {e}")
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "risk_assessment": "High",
            }

    # ==================== CYCLE 5: VEILLE (MONITORING) ====================

    def monitor_position(
        self, symbol: str, trade_context: Dict[str, Any], current_price: float
    ) -> Dict[str, Any]:
        """
        Surveille une position ouverte et recherche des événements critiques
        """
        prompt = f"""You are monitoring an open position. Check for breaking news and sentiment changes.

Position:
{json.dumps(trade_context, indent=2)}

Current Price: ${current_price}

Tasks:
1. Use web_search() for "{symbol} breaking news" (last 1 hour)
2. Use x_search() for "${symbol}" (recent activity)

Evaluate:
- Any breaking news (earnings surprise, scandal, major announcement)?
- Sentiment shift detected?
- Should we take action?

Return as JSON:
{{
    "alert_level": "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "events_detected": [
        {{
            "type": "breaking_news" | "sentiment_shift" | "volume_spike",
            "description": "...",
            "severity": "low" | "medium" | "high"
        }}
    ],
    "recommended_action": "HOLD" | "EXIT_PARTIAL" | "EXIT_FULL" | "ADJUST_STOP",
    "reasoning": "Explanation",
    "sentiment_change": {{
        "before": 0.72,
        "after": 0.41
    }}
}}
"""

        try:
            chat = self.client.chat.create(
                model=self.model, messages=[user(prompt)], tools=self.agentic_tools
            )

            response_text = self._get_final_response(chat)
            monitoring = self._extract_json(response_text)

            logger.info(
                f"Monitoring {symbol}: {monitoring.get('alert_level', 'N/A')}"
            )
            return monitoring

        except Exception as e:
            logger.error(f"Erreur monitoring {symbol}: {e}")
            return {
                "alert_level": "NONE",
                "events_detected": [],
                "recommended_action": "HOLD",
                "reasoning": f"Error: {str(e)}",
            }

    # ==================== CYCLE 6: RÉFLEXION ====================

    def reflect_on_strategy(
        self, trades: List[Dict[str, Any]], current_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Réflexion sur la stratégie basée sur les trades passés
        Version améliorée avec stratégie
        """
        trades_summary = "\n\n".join(
            [
                f"Trade #{t['trade_number']}:\n"
                f"  Symbol: {t['symbol']}\n"
                f"  Action: {t['action']}\n"
                f"  Entry: ${t['entry_price']}\n"
                f"  Exit: ${t.get('exit_price', 'Still open')}\n"
                f"  P&L: ${t.get('pnl', 0):.2f} ({t.get('pnl_percentage', 0):.2f}%)\n"
                f"  Reasoning: {t.get('reasoning', {}).get('reasoning', 'N/A')}"
                for t in trades
            ]
        )

        prompt = f"""You are performing DEEP SELF-REFLECTION on your trading performance.

Analyzed {len(trades)} recent trades:
{trades_summary}

Current Strategy:
{json.dumps(current_strategy, indent=2)}

Tasks:
1. Use code_execution() to calculate detailed performance metrics
2. Identify patterns in winning vs losing trades
3. Assess if current strategy is working

Provide comprehensive reflection as JSON:
{{
    "performance_summary": {{
        "win_rate": 0.65,
        "avg_gain": 12.5,
        "avg_loss": -5.2,
        "profit_factor": 2.4,
        "max_drawdown": -8.5
    }},
    "mistakes": [
        {{
            "description": "What went wrong",
            "trades_affected": [1, 3, 5],
            "impact": "Cost us X%"
        }}
    ],
    "successes": [
        {{
            "pattern": "What worked",
            "trades_involved": [2, 4, 6],
            "why_it_worked": "Explanation"
        }}
    ],
    "strategy_assessment": {{
        "is_working": true/false,
        "strengths": ["..."],
        "weaknesses": ["..."],
        "suggested_adjustments": {{
            "entry_criteria": {{}},
            "exit_criteria": {{}},
            "risk_management": {{}}
        }}
    }},
    "new_rules": [
        {{
            "rule": "Specific rule to follow",
            "category": "entry" | "exit" | "risk_management",
            "priority": 1-5,
            "reason": "Why this rule"
        }}
    ]
}}
"""

        try:
            chat = self.client.chat.create(
                model=self.model, messages=[user(prompt)], tools=self.agentic_tools
            )

            response_text = self._get_final_response(chat)
            reflection = self._extract_json(response_text)

            logger.info("Réflexion stratégique terminée")
            return reflection

        except Exception as e:
            logger.error(f"Erreur lors de la réflexion: {e}")
            return {
                "mistakes": [],
                "successes": [],
                "new_rules": [],
                "summary": f"Error: {str(e)}",
            }

    # ==================== UTILITAIRES ====================

    def _get_final_response(self, chat) -> str:
        """Extrait la réponse finale du chat (après que Grok ait utilisé ses outils)"""
        # Pour xai-sdk >= 1.3.1, il faut appeler chat.sample() pour obtenir la réponse
        if hasattr(chat, 'sample'):
            response = chat.sample()
            if hasattr(response, 'content'):
                return response.content if isinstance(response.content, str) else str(response.content)

        # Fallback pour anciennes versions qui retournent directement un itérable
        response_text = ""
        try:
            for message in chat:
                if hasattr(message, "content") and message.content:
                    response_text += message.content
        except TypeError:
            # Si chat n'est pas itérable, essayer d'accéder directement au content
            if hasattr(chat, "content"):
                response_text = chat.content if isinstance(chat.content, str) else str(chat.content)

        return response_text

    def _extract_json(self, content: str) -> Dict:
        """Extract JSON from Grok response (handles markdown code blocks)."""
        try:
            return json.loads(content)
        except:
            # Try to extract from markdown code block
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
                return json.loads(json_str)
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                json_str = content[start:end].strip()
                return json.loads(json_str)
            else:
                # Try to find JSON object in text
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    return json.loads(json_str)
                raise ValueError("No JSON found in response")

    def _get_default_strategy(self, capital: float, risk_profile: str) -> Dict[str, Any]:
        """Stratégie par défaut si Grok échoue"""
        return {
            "style": "momentum_growth",
            "holding_period": "3-10 days",
            "description": "Default momentum and growth strategy",
            "entry_criteria": {
                "catalysts": ["earnings_beat", "product_launch"],
                "technical": ["RSI < 70", "Volume > 1.5x average"],
                "sentiment": ["positive_sentiment > 0.6"],
            },
            "exit_criteria": {
                "take_profit": "15%",
                "stop_loss": "7%",
                "trailing_stop": "5% after +10%",
            },
            "risk_management": {
                "max_position_size": 20,
                "max_positions": 5,
                "max_daily_loss": 5,
            },
            "parameters": {"sentiment_weight": 0.4, "technical_weight": 0.6},
        }


grok_service = GrokService()
