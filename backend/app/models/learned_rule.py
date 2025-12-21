from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class LearnedRule(Base):
    __tablename__ = "learned_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Reference to reflection that created this rule
    from_reflection_id = Column(Integer, ForeignKey("reflections.id"), nullable=True)

    # Rule metadata
    category = Column(String, nullable=True)  # e.g., "risk_management", "entry", "exit"
    priority = Column(Integer, default=1)  # 1-5, higher = more important

    # Active status
    is_active = Column(Boolean, default=True)

    # Performance tracking
    times_applied = Column(Integer, default=0)
    success_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<LearnedRule {self.id}: {self.rule[:50]}...>"
