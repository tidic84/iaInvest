from sqlalchemy import Column, Integer, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Portfolio values
    total_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)

    # Positions (JSON array)
    positions = Column(JSON, nullable=True)  # List of current positions

    # Performance metrics
    total_pnl = Column(Float, default=0.0)
    total_pnl_percentage = Column(Float, default=0.0)

    # Daily metrics
    daily_pnl = Column(Float, default=0.0)
    daily_trades = Column(Integer, default=0)

    # Statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    # Risk metrics
    current_drawdown = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)

    def __repr__(self):
        return f"<PortfolioSnapshot {self.timestamp}: ${self.total_value:.2f}>"
