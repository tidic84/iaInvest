from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base


class TradingStrategy(Base):
    __tablename__ = "trading_strategies"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)

    # Strategy definition
    style = Column(String, nullable=False)  # "momentum", "growth", "value", etc.
    description = Column(String, nullable=True)

    # Strategy rules (JSON)
    entry_criteria = Column(JSON, nullable=False)
    exit_criteria = Column(JSON, nullable=False)
    risk_management = Column(JSON, nullable=False)

    # Additional parameters
    parameters = Column(JSON, nullable=True)

    # Performance tracking
    performance_metrics = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<TradingStrategy v{self.version}: {self.style} (active={self.is_active})>"
