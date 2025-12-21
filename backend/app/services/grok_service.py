import json
import os
from xai_sdk import Client
from xai_sdk.chat import user, assistant
from app.config import settings
from typing import Dict, List, Any, Optional
from loguru import logger


class GrokService:
    def __init__(self):
        self.client = Client(api_key=settings.XAI_API_KEY)
        self.model = settings.GROK_MODEL

    def analyze_market(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict[str, Any],
        sentiment_data: Optional[Dict] = None,
        learned_rules: List[str] = None
    ) -> Dict[str, Any]:
        """
        Ask Grok to analyze market and decide on trade action.
        """
        learned_rules_str = "\n".join(f"- {rule}" for rule in (learned_rules or []))

        prompt = f"""You are an expert trading AI. Analyze the following market data and decide whether to BUY, SELL, or HOLD.

Symbol: {symbol}
Current Price: ${current_price}

Technical Indicators:
{json.dumps(indicators, indent=2)}

Sentiment Data:
{json.dumps(sentiment_data or {}, indent=2)}

Learned Rules (from past experience):
{learned_rules_str if learned_rules_str else "No rules learned yet."}

Based on this data, provide your trading decision as a JSON object with the following structure:
{{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0.0 to 1.0,
    "reasoning": "Detailed explanation of your decision",
    "risk_assessment": "Low" | "Medium" | "High",
    "position_size_pct": 10-20 (percentage of available capital),
    "stop_loss_pct": 3-7 (percentage below entry),
    "take_profit_pct": 8-15 (percentage above entry)
}}

Respond ONLY with the JSON object, no other text.
"""

        try:
            chat = self.client.chat.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI trading agent. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Get the response
            response_text = ""
            for message in chat:
                if hasattr(message, 'content') and message.content:
                    response_text += message.content

            logger.info(f"Grok response for {symbol}: {response_text[:200]}...")

            # Parse JSON from response
            decision = self._extract_json(response_text)
            return decision

        except Exception as e:
            logger.error(f"Error calling Grok API: {e}")
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Error analyzing market: {str(e)}",
                "risk_assessment": "High"
            }

    def reflect_on_trades(
        self,
        trades: List[Dict[str, Any]],
        current_rules: List[str]
    ) -> Dict[str, Any]:
        """
        Ask Grok to reflect on recent trades and learn from mistakes.
        """
        trades_summary = "\n\n".join([
            f"Trade #{t['trade_number']}:\n"
            f"  Symbol: {t['symbol']}\n"
            f"  Action: {t['action']}\n"
            f"  Entry: ${t['entry_price']}\n"
            f"  Exit: ${t.get('exit_price', 'Still open')}\n"
            f"  P&L: ${t.get('pnl', 0):.2f} ({t.get('pnl_percentage', 0):.2f}%)\n"
            f"  Reasoning: {t.get('reasoning', {}).get('reasoning', 'N/A')}"
            for t in trades
        ])

        current_rules_str = "\n".join(f"- {rule}" for rule in (current_rules or []))

        prompt = f"""You are an expert trading AI performing SELF-REFLECTION on your recent trading performance.

Analyze these {len(trades)} recent trades and identify:
1. Mistakes you made (overtrading, ignoring signals, poor risk management, etc.)
2. Successful patterns that worked well
3. New rules you should follow going forward

Recent Trades:
{trades_summary}

Current Rules:
{current_rules_str if current_rules_str else "No rules yet."}

Provide your reflection as a JSON object:
{{
    "mistakes": [
        {{
            "description": "What mistake was made",
            "trades_affected": [trade numbers],
            "impact": "How it affected performance"
        }}
    ],
    "successes": [
        {{
            "pattern": "What worked well",
            "trades_involved": [trade numbers],
            "why_it_worked": "Explanation"
        }}
    ],
    "new_rules": [
        {{
            "rule": "Clear rule to follow",
            "category": "entry" | "exit" | "risk_management" | "position_sizing",
            "priority": 1-5
        }}
    ],
    "strategy_adjustments": {{
        "sentiment_weight": 0.0-1.0,
        "technical_weight": 0.0-1.0,
        "risk_tolerance": "conservative" | "moderate" | "aggressive"
    }},
    "summary": "Overall assessment of these trades"
}}

Respond ONLY with the JSON object, no other text.
"""

        try:
            chat = self.client.chat.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI trading agent performing self-reflection. Be honest and critical. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Get the response
            response_text = ""
            for message in chat:
                if hasattr(message, 'content') and message.content:
                    response_text += message.content

            logger.info(f"Grok reflection completed: {response_text[:200]}...")

            reflection = self._extract_json(response_text)
            return reflection

        except Exception as e:
            logger.error(f"Error in Grok reflection: {e}")
            return {
                "mistakes": [],
                "successes": [],
                "new_rules": [],
                "summary": f"Error during reflection: {str(e)}"
            }

    def _extract_json(self, content: str) -> Dict:
        """Extract JSON from Grok response (handles markdown code blocks)."""
        try:
            # Try direct parse first
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


grok_service = GrokService()
