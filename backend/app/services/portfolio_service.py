from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.trade import Trade, TradeAction, TradeStatus
from app.models.portfolio_snapshot import PortfolioSnapshot
from app.config import settings
from loguru import logger


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db
        self.cash = settings.INITIAL_CAPITAL
        self.positions: Dict[str, Dict] = {}  # symbol -> {quantity, avg_price, current_value}
        self.initial_capital = settings.INITIAL_CAPITAL

    def get_current_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio state."""
        total_value = self.cash
        positions_list = []

        for symbol, position in self.positions.items():
            total_value += position['current_value']
            positions_list.append({
                "symbol": symbol,
                "quantity": position['quantity'],
                "avg_price": position['avg_price'],
                "current_value": position['current_value'],
                "pnl": position['current_value'] - (position['quantity'] * position['avg_price']),
                "pnl_pct": ((position['current_value'] / (position['quantity'] * position['avg_price'])) - 1) * 100
            })

        total_pnl = total_value - self.initial_capital
        total_pnl_pct = (total_pnl / self.initial_capital) * 100

        return {
            "cash": self.cash,
            "total_value": total_value,
            "positions": positions_list,
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl_pct,
            "num_positions": len(self.positions)
        }

    def execute_trade(
        self,
        symbol: str,
        action: TradeAction,
        quantity: float,
        price: float,
        reasoning: Dict = None
    ) -> Optional[Trade]:
        """Execute a trade and update portfolio."""
        try:
            if action == TradeAction.BUY:
                cost = quantity * price
                if cost > self.cash:
                    logger.warning(f"Insufficient funds for {symbol}. Need ${cost}, have ${self.cash}")
                    return None

                # Deduct cash
                self.cash -= cost

                # Add to positions
                if symbol in self.positions:
                    # Update average price
                    current_qty = self.positions[symbol]['quantity']
                    current_avg = self.positions[symbol]['avg_price']
                    new_avg = ((current_qty * current_avg) + (quantity * price)) / (current_qty + quantity)
                    self.positions[symbol]['quantity'] += quantity
                    self.positions[symbol]['avg_price'] = new_avg
                else:
                    self.positions[symbol] = {
                        'quantity': quantity,
                        'avg_price': price,
                        'current_value': quantity * price
                    }

                logger.info(f"BUY executed: {quantity} {symbol} @ ${price}")

            elif action == TradeAction.SELL:
                if symbol not in self.positions:
                    logger.warning(f"Cannot sell {symbol}, no position held")
                    return None

                if self.positions[symbol]['quantity'] < quantity:
                    logger.warning(f"Insufficient {symbol} to sell. Have {self.positions[symbol]['quantity']}, trying to sell {quantity}")
                    return None

                # Calculate P&L
                avg_price = self.positions[symbol]['avg_price']
                proceeds = quantity * price

                # Add cash
                self.cash += proceeds

                # Update position
                self.positions[symbol]['quantity'] -= quantity
                if self.positions[symbol]['quantity'] <= 0:
                    del self.positions[symbol]

                logger.info(f"SELL executed: {quantity} {symbol} @ ${price}")

            # Create trade record
            trade_count = self.db.query(Trade).count()
            trade = Trade(
                trade_number=trade_count + 1,
                action=action,
                symbol=symbol,
                quantity=quantity,
                entry_price=price,
                reasoning=reasoning,
                status=TradeStatus.CLOSED if action == TradeAction.SELL else TradeStatus.OPEN
            )

            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)

            return trade

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            self.db.rollback()
            return None

    def update_positions_value(self, prices: Dict[str, float]):
        """Update current value of all positions."""
        for symbol, position in self.positions.items():
            if symbol in prices:
                position['current_value'] = position['quantity'] * prices[symbol]

    def create_snapshot(self) -> PortfolioSnapshot:
        """Create a portfolio snapshot for charting."""
        portfolio = self.get_current_portfolio()

        # Get statistics from trades
        total_trades = self.db.query(Trade).filter(Trade.status == TradeStatus.CLOSED).count()
        winning_trades = self.db.query(Trade).filter(
            Trade.status == TradeStatus.CLOSED,
            Trade.pnl > 0
        ).count()
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        snapshot = PortfolioSnapshot(
            total_value=portfolio['total_value'],
            cash=portfolio['cash'],
            positions=portfolio['positions'],
            total_pnl=portfolio['total_pnl'],
            total_pnl_percentage=portfolio['total_pnl_pct'],
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def check_risk_limits(self) -> Dict[str, Any]:
        """Check if portfolio is within risk limits."""
        portfolio = self.get_current_portfolio()

        violations = []

        # Check max positions
        if len(self.positions) >= settings.MAX_POSITIONS:
            violations.append(f"Max positions reached: {len(self.positions)}/{settings.MAX_POSITIONS}")

        # Check drawdown
        current_drawdown = ((self.initial_capital - portfolio['total_value']) / self.initial_capital) * 100
        if current_drawdown > settings.MAX_DRAWDOWN:
            violations.append(f"Max drawdown exceeded: {current_drawdown:.2f}% > {settings.MAX_DRAWDOWN}%")

        return {
            "within_limits": len(violations) == 0,
            "violations": violations,
            "current_drawdown": current_drawdown,
            "num_positions": len(self.positions)
        }
