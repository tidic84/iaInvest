from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Trades analyzed
    trades_analyzed = Column(JSON, nullable=False)  # List of trade IDs
    start_trade_number = Column(Integer, nullable=False)
    end_trade_number = Column(Integer, nullable=False)

    # Performance metrics
    win_rate = Column(Float, nullable=True)
    avg_pnl = Column(Float, nullable=True)
    total_pnl = Column(Float, nullable=True)

    # AI Analysis
    mistakes = Column(JSON, nullable=True)  # List of identified mistakes
    successes = Column(JSON, nullable=True)  # List of successful patterns
    new_rules = Column(JSON, nullable=True)  # New rules to follow

    # Full reflection text from Grok
    full_reflection = Column(Text, nullable=True)

    # Strategy adjustments
    strategy_adjustments = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Reflection {self.id}: Trades {self.start_trade_number}-{self.end_trade_number}>"
