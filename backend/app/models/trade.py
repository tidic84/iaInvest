from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class TradeAction(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trade_number = Column(Integer, unique=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Trade details
    action = Column(Enum(TradeAction), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)

    # Risk management
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)

    # Performance
    pnl = Column(Float, default=0.0)
    pnl_percentage = Column(Float, default=0.0)

    # Status
    status = Column(Enum(TradeStatus), default=TradeStatus.OPEN)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Reasoning (JSON from Grok)
    reasoning = Column(JSON, nullable=True)

    # Technical indicators at trade time
    indicators = Column(JSON, nullable=True)

    # Sentiment data
    sentiment_score = Column(Float, nullable=True)

    # Trade metadata
    trade_metadata = Column(JSON, nullable=True)

    # Strategy and watchlist references (for autonomous trader)
    strategy_id = Column(Integer, ForeignKey("trading_strategies.id"), nullable=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlist.id"), nullable=True, index=True)

    # Exit reason (for tracking why trades are closed)
    exit_reason = Column(String, nullable=True)

    def __repr__(self):
        return f"<Trade {self.trade_number}: {self.action} {self.symbol} @ {self.entry_price}>"
