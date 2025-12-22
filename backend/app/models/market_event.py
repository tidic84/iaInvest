from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class EventType(str, enum.Enum):
    EARNINGS = "earnings"
    NEWS = "news"
    SENTIMENT_CHANGE = "sentiment_change"
    TECHNICAL_SIGNAL = "technical_signal"
    VOLUME_SPIKE = "volume_spike"
    PRICE_ALERT = "price_alert"
    OTHER = "other"


class EventSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionTaken(str, enum.Enum):
    NONE = "none"
    EXIT_FULL = "exit_full"
    EXIT_PARTIAL = "exit_partial"
    ADJUST_STOP = "adjust_stop"
    TAKE_PROFIT = "take_profit"
    HOLD = "hold"
    OTHER = "other"


class MarketEvent(Base):
    __tablename__ = "market_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Event classification
    event_type = Column(Enum(EventType), nullable=False, index=True)
    severity = Column(Enum(EventSeverity), nullable=False)

    # Event details
    symbol = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    source = Column(String, nullable=False)  # "web_search", "x_search", "technical_analysis"

    # Impact and action
    impact_assessment = Column(String, nullable=True)
    action_taken = Column(Enum(ActionTaken), default=ActionTaken.NONE)

    # Related trade
    related_trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True, index=True)

    # Additional data
    extra_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<MarketEvent {self.symbol}: {self.event_type.value} ({self.severity.value})>"
