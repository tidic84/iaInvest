"""
Trading Agent - Orchestrateur autonome des 6 cycles de trading
"""
import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from loguru import logger

from app.services.grok_service import grok_service
from app.services.market_data_service import market_data_service
from app.services.portfolio_service import PortfolioService
from app.services.strategy_service import StrategyService
from app.services.discovery_service import DiscoveryService
from app.services.monitoring_service import MonitoringService

from app.models.trade import Trade, TradeAction, TradeStatus
from app.models.trading_strategy import TradingStrategy
from app.models.watchlist import Watchlist, WatchlistStatus, WatchlistPriority
from app.models.market_event import MarketEvent, EventType, EventSeverity, ActionTaken
from app.models.learned_rule import LearnedRule
from app.models.reflection import Reflection

from app.config import settings


class TradingAgent:
    """
    Agent de trading autonome orchestrant les 6 cycles:
    1. STRATÉGIE: Définit et maintient la stratégie
    2. DÉCOUVERTE: Recherche d'opportunités (web_search + x_search)
    3. ANALYSE: Analyse approfondie des symboles sur watchlist
    4. TRADING: Exécution des trades
    5. MONITORING: Surveillance des positions ouvertes
    6. RÉFLEXION: Apprentissage et amélioration
    """

    def __init__(self, db: Session):
        self.db = db
        self.portfolio = PortfolioService(db)
        self.strategy_service = StrategyService(db)
        self.discovery_service = DiscoveryService(db)
        self.monitoring_service = MonitoringService(db)

        self.is_running = False
        self.activity_log = []

        # Cycle timers
        self.last_discovery = None
        self.last_analysis = None
        self.last_monitoring = None
        self.last_reflection_check = None

        # Active strategy
        self.current_strategy = None

    def log_activity(self, message: str, level: str = "INFO"):
        """Log activity for frontend stream."""
        timestamp = datetime.now().isoformat()
        log_entry = {"timestamp": timestamp, "level": level, "message": message}
        self.activity_log.append(log_entry)

        # Keep only last 500 logs
        if len(self.activity_log) > 500:
            self.activity_log = self.activity_log[-500:]

        logger.info(f"[Agent] {message}")

    # ==================== MAIN LOOP ====================

    async def run(self):
        """Main autonomous trading loop."""
        self.is_running = True
        self.log_activity("🚀 Autonomous Trading Agent Started", "INFO")

        try:
            # CYCLE 1: Initialize or load strategy
            await self._initialize_strategy()

            # Start concurrent cycles
            tasks = [
                asyncio.create_task(self._discovery_loop()),
                asyncio.create_task(self._analysis_loop()),
                asyncio.create_task(self._monitoring_loop()),
                asyncio.create_task(self._reflection_loop()),
            ]

            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error in main trading loop: {e}")
            self.log_activity(f"❌ Critical error: {str(e)}", "ERROR")

    # ==================== CYCLE 1: STRATÉGIE ====================

    async def _initialize_strategy(self):
        """Initialize or load trading strategy."""
        self.log_activity("📋 Initializing trading strategy...", "INFO")

        # Try to load existing active strategy
        self.current_strategy = self.strategy_service.get_active_strategy()

        if self.current_strategy:
            self.log_activity(
                f"✅ Loaded strategy v{self.current_strategy.version}: {self.current_strategy.style}",
                "INFO",
            )
        else:
            # Create new strategy with Grok
            if settings.AUTO_STRATEGY_CREATION:
                self.log_activity("🤖 Asking Grok to create a strategy...", "INFO")
                portfolio = self.portfolio.get_current_portfolio()
                capital = portfolio["total_value"]

                strategy_data = grok_service.create_trading_strategy(
                    capital=capital, risk_profile=settings.STRATEGY_RISK_PROFILE
                )

                # Save strategy
                self.current_strategy = self.strategy_service.create_strategy(
                    style=strategy_data.get("style", "momentum_growth"),
                    description=strategy_data.get("description", ""),
                    entry_criteria=strategy_data.get("entry_criteria", {}),
                    exit_criteria=strategy_data.get("exit_criteria", {}),
                    risk_management=strategy_data.get("risk_management", {}),
                    parameters=strategy_data.get("parameters", {}),
                )

                self.log_activity(
                    f"✅ Strategy created: {self.current_strategy.style}", "SUCCESS"
                )
            else:
                self.log_activity(
                    "⚠️ No active strategy and auto-creation disabled", "WARNING"
                )

    # ==================== CYCLE 2: DÉCOUVERTE ====================

    async def _discovery_loop(self):
        """Discovery loop - searches for opportunities."""
        while self.is_running:
            try:
                if self._should_run_discovery():
                    await self._run_discovery()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                await asyncio.sleep(300)

    def _should_run_discovery(self) -> bool:
        """Check if we should run discovery cycle."""
        if not self.last_discovery:
            return True
        elapsed = (datetime.now() - self.last_discovery).total_seconds()
        return elapsed >= settings.DISCOVERY_INTERVAL

    async def _run_discovery(self):
        """Run discovery cycle."""
        self.log_activity("🔍 Starting discovery cycle...", "INFO")
        self.last_discovery = datetime.now()

        try:
            # Ask Grok to discover opportunities
            discovery_result = grok_service.discover_opportunities()
            opportunities = discovery_result.get("opportunities", [])
            full_analysis = discovery_result.get("full_analysis", "")

            self.log_activity(
                f"📊 Discovery found {len(opportunities)} opportunities", "INFO"
            )

            # Log the full Grok discovery analysis
            if full_analysis and len(full_analysis) > 100:  # Only log if substantial
                self.log_activity(
                    f"📝 Grok Discovery Analysis:\n{full_analysis}", "INFO"
                )

            # Add to watchlist
            min_score = settings.MIN_OPPORTUNITY_SCORE
            added_count = 0

            for opp in opportunities:
                score = opp.get("score", 0)
                if score >= min_score:
                    priority = (
                        WatchlistPriority.HIGH
                        if score >= 8.0
                        else WatchlistPriority.MEDIUM if score >= 6.5 else WatchlistPriority.LOW
                    )

                    self.discovery_service.add_to_watchlist(
                        symbol=opp.get("symbol", ""),
                        score=score,
                        reason=opp.get("reason", ""),
                        sources=opp.get("sources", {}),
                        priority=priority,
                    )
                    added_count += 1

            self.log_activity(
                f"✅ Added {added_count} symbols to watchlist (min score: {min_score})",
                "SUCCESS",
            )

            # Cleanup old low-priority items
            removed = self.discovery_service.cleanup_old_items(
                days=settings.AUTO_REMOVE_LOW_PRIORITY_DAYS
            )
            if removed > 0:
                self.log_activity(f"🧹 Cleaned up {removed} old watchlist items", "INFO")

        except Exception as e:
            logger.error(f"Error in discovery: {e}")
            self.log_activity(f"❌ Discovery error: {str(e)}", "ERROR")

    # ==================== CYCLE 3: ANALYSE ====================

    async def _analysis_loop(self):
        """Analysis loop - analyzes watchlist items."""
        while self.is_running:
            try:
                if self._should_run_analysis():
                    await self._run_analysis()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(300)

    def _should_run_analysis(self) -> bool:
        """Check if we should run analysis cycle."""
        if not self.last_analysis:
            return True
        elapsed = (datetime.now() - self.last_analysis).total_seconds()
        return elapsed >= settings.ANALYSIS_INTERVAL

    async def _run_analysis(self):
        """Run analysis cycle."""
        self.log_activity("📈 Starting analysis cycle...", "INFO")
        self.last_analysis = datetime.now()

        if not self.current_strategy:
            self.log_activity("⚠️ No active strategy for analysis", "WARNING")
            return

        try:
            # Get watchlist items to analyze
            watchlist = self.discovery_service.get_watchlist(
                status=WatchlistStatus.WATCHING
            )

            self.log_activity(f"🔎 Analyzing {len(watchlist)} symbols...", "INFO")

            for item in watchlist[:10]:  # Limit to top 10
                await self._analyze_symbol(item)
                await asyncio.sleep(5)  # Small delay between analyses

        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            self.log_activity(f"❌ Analysis error: {str(e)}", "ERROR")

    async def _analyze_symbol(self, watchlist_item: Watchlist):
        """Analyze a single symbol."""
        try:
            symbol = watchlist_item.symbol
            self.log_activity(f"🔬 Deep analysis of {symbol}...", "INFO")

            # Update status to ANALYZING
            self.discovery_service.update_watchlist_status(
                watchlist_item.id, WatchlistStatus.ANALYZING
            )

            # Prepare context
            watchlist_context = {
                "symbol": symbol,
                "score": watchlist_item.score,
                "reason": watchlist_item.reason,
                "sources": watchlist_item.sources,
                "added_at": watchlist_item.added_at.isoformat(),
            }

            strategy_dict = {
                "style": self.current_strategy.style,
                "entry_criteria": self.current_strategy.entry_criteria,
                "exit_criteria": self.current_strategy.exit_criteria,
                "risk_management": self.current_strategy.risk_management,
            }

            # Ask Grok to analyze
            analysis = grok_service.deep_analyze_symbol(
                symbol=symbol, watchlist_context=watchlist_context, strategy=strategy_dict
            )

            decision = analysis.get("decision", "HOLD")
            confidence = analysis.get("confidence", 0.0)
            full_analysis = analysis.get("full_analysis", "")

            self.log_activity(
                f"💡 {symbol}: {decision} (confidence: {confidence:.2f})", "INFO"
            )

            # Log the full Grok analysis for this symbol
            if full_analysis and len(full_analysis) > 100:  # Only log if substantial
                self.log_activity(
                    f"📝 Grok Analysis for {symbol}:\n{full_analysis}", "INFO"
                )

            # Handle decision
            if decision == "BUY" and confidence >= 0.6:
                # Execute trade
                await self._execute_trade_from_analysis(symbol, analysis, watchlist_item)
            elif decision == "REMOVE":
                # Remove from watchlist
                self.discovery_service.remove_from_watchlist(watchlist_item.id)
                self.log_activity(f"🗑️ Removed {symbol} from watchlist", "INFO")
            else:
                # Back to WATCHING
                self.discovery_service.update_watchlist_status(
                    watchlist_item.id, WatchlistStatus.WATCHING
                )

        except Exception as e:
            symbol_name = getattr(watchlist_item, 'symbol', 'UNKNOWN')
            logger.error(f"Error analyzing {symbol_name}: {e}")
            self.log_activity(f"❌ Error analyzing {symbol_name}: {str(e)}", "ERROR")

    async def _execute_trade_from_analysis(
        self, symbol: str, analysis: Dict, watchlist_item: Watchlist
    ):
        """Execute a trade based on analysis."""
        try:
            # Get current price
            current_price = market_data_service.get_current_price(symbol)
            if not current_price:
                self.log_activity(f"⚠️ Cannot get price for {symbol}", "WARNING")
                return

            # Calculate position size
            portfolio = self.portfolio.get_current_portfolio()
            max_position_size = self.current_strategy.risk_management.get(
                "max_position_size", 20
            )
            position_size_pct = min(
                analysis.get("position_size_pct", 15), max_position_size
            )

            position_value = portfolio["total_value"] * (position_size_pct / 100)
            position_value = min(position_value, portfolio["cash"])

            quantity = position_value / current_price

            if quantity <= 0:
                self.log_activity(f"⚠️ Insufficient funds to buy {symbol}", "WARNING")
                return

            # Calculate stop-loss and take-profit
            stop_loss_pct = analysis.get("stop_loss_pct", 7)
            take_profit_pct = analysis.get("take_profit_pct", 15)

            stop_loss = current_price * (1 - stop_loss_pct / 100)
            take_profit = current_price * (1 + take_profit_pct / 100)

            # Execute trade
            trade = self.portfolio.execute_trade(
                symbol=symbol,
                action=TradeAction.BUY,
                quantity=quantity,
                price=current_price,
                reasoning=analysis,
                stop_loss=stop_loss,
                take_profit=take_profit,
            )

            if trade:
                # Link to strategy and watchlist
                trade.strategy_id = self.current_strategy.id
                trade.watchlist_id = watchlist_item.id
                self.db.commit()

                # Mark watchlist item as traded
                self.discovery_service.mark_as_traded(watchlist_item.id)

                self.log_activity(
                    f"✅ BUY: {quantity:.4f} {symbol} @ ${current_price:.2f} "
                    f"(SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})",
                    "SUCCESS",
                )

        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            self.log_activity(f"❌ Error executing trade: {str(e)}", "ERROR")

    # ==================== CYCLE 5: MONITORING ====================

    async def _monitoring_loop(self):
        """Monitoring loop - watches open positions."""
        while self.is_running:
            try:
                if self._should_run_monitoring():
                    await self._run_monitoring()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(180)

    def _should_run_monitoring(self) -> bool:
        """Check if we should run monitoring cycle."""
        if not self.last_monitoring:
            return True
        elapsed = (datetime.now() - self.last_monitoring).total_seconds()
        return elapsed >= settings.MONITORING_INTERVAL

    async def _run_monitoring(self):
        """Run monitoring cycle."""
        self.last_monitoring = datetime.now()

        try:
            # Get open trades
            open_trades = (
                self.db.query(Trade).filter(Trade.status == TradeStatus.OPEN).all()
            )

            if not open_trades:
                return

            self.log_activity(f"👁️ Monitoring {len(open_trades)} positions...", "INFO")

            for trade in open_trades:
                await self._monitor_position(trade)
                await asyncio.sleep(3)

        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            self.log_activity(f"❌ Monitoring error: {str(e)}", "ERROR")

    async def _monitor_position(self, trade: Trade):
        """Monitor a single position."""
        symbol = trade.symbol

        try:
            # Get current price
            current_price = market_data_service.get_current_price(symbol)
            if not current_price:
                return

            # Check price alerts
            alerts = self.monitoring_service.check_position_alerts(trade, current_price)

            for alert in alerts:
                # Create event
                severity_map = {
                    "LOW": EventSeverity.LOW,
                    "MEDIUM": EventSeverity.MEDIUM,
                    "HIGH": EventSeverity.HIGH,
                }
                severity = severity_map.get(alert["severity"], EventSeverity.MEDIUM)

                event = self.monitoring_service.create_event(
                    symbol=symbol,
                    event_type=EventType.PRICE_ALERT,
                    severity=severity,
                    description=alert["message"],
                    source="monitoring_service",
                    related_trade_id=trade.id,
                    extra_data=alert.get("details", {}),
                )

                self.log_activity(f"⚠️ {alert['message']}", "WARNING")

                # Handle critical alerts
                if alert["type"] == "stop_loss_hit":
                    await self._close_position(
                        trade, current_price, "Stop-loss triggered"
                    )
                elif alert["type"] == "take_profit_hit":
                    await self._close_position(
                        trade, current_price, "Take-profit reached"
                    )

            # Ask Grok to monitor for breaking news
            trade_context = {
                "symbol": symbol,
                "entry_price": trade.entry_price,
                "current_price": current_price,
                "quantity": trade.quantity,
                "pnl_pct": ((current_price - trade.entry_price) / trade.entry_price)
                * 100,
            }

            monitoring_result = grok_service.monitor_position(
                symbol=symbol, trade_context=trade_context, current_price=current_price
            )

            alert_level = monitoring_result.get("alert_level", "NONE")

            if alert_level in ["HIGH", "CRITICAL"]:
                # Log events
                for event_data in monitoring_result.get("events_detected", []):
                    severity = EventSeverity.HIGH if alert_level == "CRITICAL" else EventSeverity.MEDIUM
                    self.monitoring_service.create_event(
                        symbol=symbol,
                        event_type=EventType.NEWS,
                        severity=severity,
                        description=event_data.get("description", ""),
                        source="grok_monitoring",
                        related_trade_id=trade.id,
                    )

                self.log_activity(
                    f"🚨 {symbol}: {alert_level} - {monitoring_result.get('reasoning', '')}",
                    "WARNING",
                )

                # Handle recommendation
                action = monitoring_result.get("recommended_action", "HOLD")
                if action == "EXIT_FULL":
                    await self._close_position(
                        trade, current_price, monitoring_result.get("reasoning", "")
                    )
                elif action == "EXIT_PARTIAL":
                    # Close 50% of position
                    await self._close_position(
                        trade,
                        current_price,
                        "Partial exit: " + monitoring_result.get("reasoning", ""),
                        partial_pct=0.5,
                    )

        except Exception as e:
            logger.error(f"Error monitoring {symbol}: {e}")

    async def _close_position(
        self,
        trade: Trade,
        exit_price: float,
        reason: str,
        partial_pct: float = 1.0,
    ):
        """Close a position (full or partial)."""
        try:
            symbol = trade.symbol
            quantity = trade.quantity * partial_pct

            # Execute sell
            sell_trade = self.portfolio.execute_trade(
                symbol=symbol,
                action=TradeAction.SELL,
                quantity=quantity,
                price=exit_price,
                reasoning={"reason": reason},
            )

            if sell_trade:
                # Calculate P&L
                pnl = (exit_price - trade.entry_price) * quantity
                pnl_pct = ((exit_price / trade.entry_price) - 1) * 100

                # Update original trade
                if partial_pct >= 1.0:
                    trade.status = TradeStatus.CLOSED
                    trade.closed_at = datetime.now()

                trade.exit_price = exit_price
                trade.pnl = pnl
                trade.pnl_percentage = pnl_pct
                trade.exit_reason = reason
                self.db.commit()

                action_type = "FULL EXIT" if partial_pct >= 1.0 else f"PARTIAL EXIT ({partial_pct*100:.0f}%)"
                self.log_activity(
                    f"✅ {action_type}: {quantity:.4f} {symbol} @ ${exit_price:.2f} | "
                    f"P&L: ${pnl:.2f} ({pnl_pct:.2f}%) | Reason: {reason}",
                    "SUCCESS",
                )

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            self.log_activity(f"❌ Error closing position: {str(e)}", "ERROR")

    # ==================== CYCLE 6: RÉFLEXION ====================

    async def _reflection_loop(self):
        """Reflection loop - learns from trades."""
        while self.is_running:
            try:
                if self._should_run_reflection():
                    await self._run_reflection()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in reflection loop: {e}")
                await asyncio.sleep(600)

    def _should_run_reflection(self) -> bool:
        """Check if we should run reflection."""
        if not settings.REFLECTION_ENABLED:
            return False

        # Count closed trades since last reflection
        last_reflection = (
            self.db.query(Reflection).order_by(Reflection.timestamp.desc()).first()
        )

        if last_reflection:
            trades_since = (
                self.db.query(Trade)
                .filter(
                    Trade.status == TradeStatus.CLOSED,
                    Trade.timestamp > last_reflection.timestamp,
                )
                .count()
            )
        else:
            trades_since = (
                self.db.query(Trade).filter(Trade.status == TradeStatus.CLOSED).count()
            )

        return trades_since >= settings.REFLECTION_TRADES_THRESHOLD

    async def _run_reflection(self):
        """Run reflection cycle."""
        self.log_activity("🧠 Starting reflection cycle...", "INFO")

        try:
            # Get recent closed trades
            trades = (
                self.db.query(Trade)
                .filter(Trade.status == TradeStatus.CLOSED)
                .order_by(Trade.timestamp.desc())
                .limit(settings.REFLECTION_TRADES_THRESHOLD)
                .all()
            )

            if not trades:
                return

            # Convert to dict
            trades_data = [
                {
                    "trade_number": t.trade_number,
                    "symbol": t.symbol,
                    "action": t.action.value,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "pnl": t.pnl or 0,
                    "pnl_percentage": t.pnl_percentage or 0,
                    "reasoning": t.reasoning or {},
                    "exit_reason": t.exit_reason,
                }
                for t in trades
            ]

            # Get current strategy
            strategy_dict = {
                "style": self.current_strategy.style,
                "entry_criteria": self.current_strategy.entry_criteria,
                "exit_criteria": self.current_strategy.exit_criteria,
                "risk_management": self.current_strategy.risk_management,
                "parameters": self.current_strategy.parameters,
            }

            # Ask Grok to reflect
            reflection_data = grok_service.reflect_on_strategy(
                trades=trades_data, current_strategy=strategy_dict
            )

            # Save reflection
            reflection = Reflection(
                trades_analyzed=[t.id for t in trades],
                start_trade_number=trades[-1].trade_number,
                end_trade_number=trades[0].trade_number,
                mistakes=reflection_data.get("mistakes", []),
                successes=reflection_data.get("successes", []),
                new_rules=reflection_data.get("new_rules", []),
                full_reflection=reflection_data.get("summary", ""),
                strategy_adjustments=reflection_data.get("strategy_assessment", {}),
            )
            self.db.add(reflection)
            self.db.commit()
            self.db.refresh(reflection)

            # Add new learned rules
            for rule_data in reflection_data.get("new_rules", []):
                rule = LearnedRule(
                    rule=rule_data.get("rule", ""),
                    category=rule_data.get("category", "general"),
                    priority=rule_data.get("priority", 3),
                    from_reflection_id=reflection.id,
                )
                self.db.add(rule)

            self.db.commit()

            # Update strategy performance
            perf_summary = reflection_data.get("performance_summary", {})
            self.strategy_service.update_strategy_performance(
                self.current_strategy.id, perf_summary
            )

            self.log_activity(
                f"✅ Reflection complete: {len(reflection_data.get('mistakes', []))} mistakes, "
                f"{len(reflection_data.get('new_rules', []))} new rules",
                "SUCCESS",
            )

            # Check if strategy needs adjustment
            assessment = reflection_data.get("strategy_assessment", {})
            if not assessment.get("is_working", True):
                self.log_activity(
                    "⚠️ Strategy may need adjustment - review recommended", "WARNING"
                )

        except Exception as e:
            logger.error(f"Error in reflection: {e}")
            self.log_activity(f"❌ Reflection error: {str(e)}", "ERROR")

    # ==================== CONTROL ====================

    def stop(self):
        """Stop the trading agent."""
        self.is_running = False
        self.log_activity("🛑 Autonomous Trading Agent Stopped", "INFO")
