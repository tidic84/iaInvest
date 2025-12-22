from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class WatchlistPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WatchlistStatus(str, enum.Enum):
    WATCHING = "watching"
    ANALYZING = "analyzing"
    TRADED = "traded"
    REMOVED = "removed"


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    last_analyzed = Column(DateTime(timezone=True), nullable=True)

    # Scoring and priority
    score = Column(Float, nullable=False)  # 0-10
    priority = Column(Enum(WatchlistPriority), default=WatchlistPriority.MEDIUM)
    status = Column(Enum(WatchlistStatus), default=WatchlistStatus.WATCHING, index=True)

    # Context and reasoning
    reason = Column(String, nullable=False)
    sources = Column(JSON, nullable=True)  # web_search and x_search results

    # Additional data
    extra_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Watchlist {self.symbol}: score={self.score}, priority={self.priority.value}>"
