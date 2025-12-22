from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class AdjustmentType(str, enum.Enum):
    PARAMETER_CHANGE = "parameter_change"
    NEW_RULE = "new_rule"
    CRITERIA_UPDATE = "criteria_update"
    RISK_ADJUSTMENT = "risk_adjustment"
    STYLE_CHANGE = "style_change"


class AdjustmentCreator(str, enum.Enum):
    REFLECTION = "reflection"
    MANUAL = "manual"
    AUTO = "auto"


class StrategyAdjustment(Base):
    __tablename__ = "strategy_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Related strategy
    strategy_id = Column(Integer, ForeignKey("trading_strategies.id"), nullable=False, index=True)

    # Adjustment details
    adjustment_type = Column(Enum(AdjustmentType), nullable=False)
    created_by = Column(Enum(AdjustmentCreator), nullable=False)
    reason = Column(String, nullable=False)

    # Changes made
    changes = Column(JSON, nullable=False)

    # Performance tracking
    performance_before = Column(JSON, nullable=True)
    performance_after = Column(JSON, nullable=True)  # Filled later

    def __repr__(self):
        return f"<StrategyAdjustment {self.adjustment_type.value} by {self.created_by.value}>"
