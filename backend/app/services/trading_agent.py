import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from loguru import logger

from app.services.grok_service import grok_service
from app.services.market_data_service import market_data_service
from app.services.portfolio_service import PortfolioService
from app.models.trade import Trade, TradeAction, TradeStatus
from app.models.reflection import Reflection
from app.models.learned_rule import LearnedRule
from app.config import settings


class TradingAgent:
    def __init__(self, db: Session):
        self.db = db
        self.portfolio = PortfolioService(db)
        self.is_running = False
        self.last_trade_time = None
        self.activity_log = []

    def log_activity(self, message: str, level: str = "INFO"):
        """Log activity for frontend stream."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.activity_log.append(log_entry)
        logger.info(f"[Agent] {message}")

    async def run(self):
        """Main trading loop."""
        self.is_running = True
        self.log_activity("🚀 Trading Agent Started", "INFO")

        try:
            while self.is_running:
                # Check if we should trade
                if not self._can_trade():
                    await asyncio.sleep(60)
                    continue

                # Check risk limits
                risk_check = self.portfolio.check_risk_limits()
                if not risk_check['within_limits']:
                    self.log_activity(
                        f"⚠️ Risk limits violated: {', '.join(risk_check['violations'])}",
                        "WARNING"
                    )
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue

                # Analyze each watched symbol
                for symbol in settings.watched_symbols_list:
                    await self._analyze_and_trade(symbol)
                    await asyncio.sleep(10)  # Small delay between symbols

                # Check if reflection needed
                await self._check_reflection()

                # Create portfolio snapshot
                self.portfolio.create_snapshot()

                # Wait before next iteration
                await asyncio.sleep(settings.MIN_INTERVAL_BETWEEN_TRADES)

        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            self.log_activity(f"❌ Error in trading loop: {str(e)}", "ERROR")

    async def _analyze_and_trade(self, symbol: str):
        """Analyze a symbol and execute trade if appropriate."""
        try:
            self.log_activity(f"🔍 Analyzing {symbol}...", "INFO")

            # Get current price
            current_price = market_data_service.get_current_price(symbol)
            if not current_price:
                self.log_activity(f"⚠️ Could not get price for {symbol}", "WARNING")
                return

            # Get technical indicators
            indicators = market_data_service.get_technical_indicators(symbol)
            if not indicators:
                self.log_activity(f"⚠️ Could not get indicators for {symbol}", "WARNING")
                return

            # Get learned rules
            learned_rules = self.db.query(LearnedRule).filter(
                LearnedRule.is_active == True
            ).all()
            rules_text = [rule.rule for rule in learned_rules]

            # Ask Grok for decision
            self.log_activity(f"🤖 Asking Grok for decision on {symbol}...", "INFO")
            decision = grok_service.analyze_market(
                symbol=symbol,
                current_price=current_price,
                indicators=indicators,
                sentiment_data=None,
                learned_rules=rules_text
            )

            self.log_activity(
                f"💭 Grok says: {decision['action']} (confidence: {decision.get('confidence', 0):.2f}) - {decision.get('reasoning', '')[:100]}...",
                "INFO"
            )

            # Execute trade based on decision
            if decision['action'] == 'BUY':
                await self._execute_buy(symbol, current_price, decision)
            elif decision['action'] == 'SELL':
                await self._execute_sell(symbol, current_price, decision)
            else:
                self.log_activity(f"⏸️ Holding {symbol}", "INFO")

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            self.log_activity(f"❌ Error analyzing {symbol}: {str(e)}", "ERROR")

    async def _execute_buy(self, symbol: str, price: float, decision: Dict):
        """Execute a buy trade."""
        try:
            # Calculate position size
            portfolio = self.portfolio.get_current_portfolio()
            max_position_value = portfolio['total_value'] * (settings.MAX_POSITION_SIZE_PCT / 100)
            position_value = min(max_position_value, portfolio['cash'])

            # Apply Grok's recommendation if available
            if 'position_size_pct' in decision:
                recommended_value = portfolio['total_value'] * (decision['position_size_pct'] / 100)
                position_value = min(position_value, recommended_value)

            quantity = position_value / price

            if quantity <= 0:
                self.log_activity(f"⚠️ Cannot buy {symbol}: insufficient funds", "WARNING")
                return

            # Execute trade
            trade = self.portfolio.execute_trade(
                symbol=symbol,
                action=TradeAction.BUY,
                quantity=quantity,
                price=price,
                reasoning=decision
            )

            if trade:
                self.log_activity(
                    f"✅ BUY: {quantity:.4f} {symbol} @ ${price:.2f} (${position_value:.2f})",
                    "SUCCESS"
                )
                self.last_trade_time = datetime.now()

        except Exception as e:
            logger.error(f"Error executing buy: {e}")
            self.log_activity(f"❌ Error executing buy: {str(e)}", "ERROR")

    async def _execute_sell(self, symbol: str, price: float, decision: Dict):
        """Execute a sell trade."""
        try:
            if symbol not in self.portfolio.positions:
                self.log_activity(f"⚠️ Cannot sell {symbol}: no position held", "WARNING")
                return

            quantity = self.portfolio.positions[symbol]['quantity']

            # Execute trade
            trade = self.portfolio.execute_trade(
                symbol=symbol,
                action=TradeAction.SELL,
                quantity=quantity,
                price=price,
                reasoning=decision
            )

            if trade:
                # Calculate P&L
                avg_price = self.portfolio.positions.get(symbol, {}).get('avg_price', price)
                pnl = (price - avg_price) * quantity
                pnl_pct = ((price / avg_price) - 1) * 100

                # Update trade P&L
                trade.exit_price = price
                trade.pnl = pnl
                trade.pnl_percentage = pnl_pct
                trade.closed_at = datetime.now()
                self.db.commit()

                self.log_activity(
                    f"✅ SELL: {quantity:.4f} {symbol} @ ${price:.2f} | P&L: ${pnl:.2f} ({pnl_pct:.2f}%)",
                    "SUCCESS"
                )
                self.last_trade_time = datetime.now()

        except Exception as e:
            logger.error(f"Error executing sell: {e}")
            self.log_activity(f"❌ Error executing sell: {str(e)}", "ERROR")

    async def _check_reflection(self):
        """Check if it's time for auto-reflection."""
        if not settings.REFLECTION_ENABLED:
            return

        # Count closed trades since last reflection
        last_reflection = self.db.query(Reflection).order_by(
            Reflection.timestamp.desc()
        ).first()

        if last_reflection:
            trades_since = self.db.query(Trade).filter(
                Trade.status == TradeStatus.CLOSED,
                Trade.timestamp > last_reflection.timestamp
            ).count()
        else:
            trades_since = self.db.query(Trade).filter(
                Trade.status == TradeStatus.CLOSED
            ).count()

        if trades_since >= settings.REFLECTION_INTERVAL:
            await self._perform_reflection()

    async def _perform_reflection(self):
        """Perform auto-reflection on recent trades."""
        try:
            self.log_activity("🧠 Starting auto-reflection...", "INFO")

            # Get recent trades
            trades = self.db.query(Trade).filter(
                Trade.status == TradeStatus.CLOSED
            ).order_by(Trade.timestamp.desc()).limit(settings.REFLECTION_INTERVAL).all()

            if not trades:
                return

            # Convert trades to dict
            trades_data = [
                {
                    "trade_number": t.trade_number,
                    "symbol": t.symbol,
                    "action": t.action.value,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "pnl": t.pnl,
                    "pnl_percentage": t.pnl_percentage,
                    "reasoning": t.reasoning
                }
                for t in trades
            ]

            # Get current rules
            current_rules = self.db.query(LearnedRule).filter(
                LearnedRule.is_active == True
            ).all()
            rules_text = [rule.rule for rule in current_rules]

            # Ask Grok to reflect
            reflection_data = grok_service.reflect_on_trades(trades_data, rules_text)

            # Save reflection
            reflection = Reflection(
                trades_analyzed=[t.id for t in trades],
                start_trade_number=trades[-1].trade_number,
                end_trade_number=trades[0].trade_number,
                mistakes=reflection_data.get('mistakes', []),
                successes=reflection_data.get('successes', []),
                new_rules=reflection_data.get('new_rules', []),
                full_reflection=reflection_data.get('summary', ''),
                strategy_adjustments=reflection_data.get('strategy_adjustments', {})
            )
            self.db.add(reflection)
            self.db.commit()
            self.db.refresh(reflection)

            # Add new rules
            for rule_data in reflection_data.get('new_rules', []):
                rule = LearnedRule(
                    rule=rule_data['rule'],
                    category=rule_data.get('category', 'general'),
                    priority=rule_data.get('priority', 3),
                    from_reflection_id=reflection.id
                )
                self.db.add(rule)

            self.db.commit()

            self.log_activity(
                f"✅ Reflection complete: {len(reflection_data.get('mistakes', []))} mistakes, "
                f"{len(reflection_data.get('new_rules', []))} new rules learned",
                "SUCCESS"
            )

        except Exception as e:
            logger.error(f"Error in reflection: {e}")
            self.log_activity(f"❌ Error in reflection: {str(e)}", "ERROR")

    def _can_trade(self) -> bool:
        """Check if we can trade now (rate limiting)."""
        if not self.last_trade_time:
            return True

        time_since_last = (datetime.now() - self.last_trade_time).total_seconds()
        return time_since_last >= settings.MIN_INTERVAL_BETWEEN_TRADES

    def stop(self):
        """Stop the trading agent."""
        self.is_running = False
        self.log_activity("🛑 Trading Agent Stopped", "INFO")
