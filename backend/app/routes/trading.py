from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.trade import Trade
from app.models.reflection import Reflection
from app.models.learned_rule import LearnedRule
from app.models.portfolio_snapshot import PortfolioSnapshot
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["trading"])


class TradingStatus(BaseModel):
    is_running: bool
    last_trade_time: str = None
    num_trades: int
    portfolio_value: float


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@router.get("/trades")
async def get_trades(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent trades."""
    trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": t.id,
            "trade_number": t.trade_number,
            "timestamp": t.timestamp.isoformat(),
            "action": t.action.value,
            "symbol": t.symbol,
            "quantity": t.quantity,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "pnl": t.pnl,
            "pnl_percentage": t.pnl_percentage,
            "status": t.status.value,
            "reasoning": t.reasoning
        }
        for t in trades
    ]


@router.get("/reflections")
async def get_reflections(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent reflections."""
    reflections = db.query(Reflection).order_by(Reflection.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "start_trade_number": r.start_trade_number,
            "end_trade_number": r.end_trade_number,
            "mistakes": r.mistakes,
            "successes": r.successes,
            "new_rules": r.new_rules,
            "full_reflection": r.full_reflection
        }
        for r in reflections
    ]


@router.get("/rules")
async def get_learned_rules(active_only: bool = True, db: Session = Depends(get_db)):
    """Get learned rules."""
    query = db.query(LearnedRule)
    if active_only:
        query = query.filter(LearnedRule.is_active == True)

    rules = query.order_by(LearnedRule.priority.desc(), LearnedRule.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "rule": r.rule,
            "category": r.category,
            "priority": r.priority,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat(),
            "times_applied": r.times_applied,
            "success_count": r.success_count
        }
        for r in rules
    ]


@router.get("/portfolio/current")
async def get_current_portfolio(db: Session = Depends(get_db)):
    """Get current portfolio state."""
    from app.services.portfolio_service import PortfolioService
    portfolio_service = PortfolioService(db)
    return portfolio_service.get_current_portfolio()


@router.get("/portfolio/history")
async def get_portfolio_history(limit: int = 100, db: Session = Depends(get_db)):
    """Get portfolio history for charts."""
    snapshots = db.query(PortfolioSnapshot).order_by(
        PortfolioSnapshot.timestamp.desc()
    ).limit(limit).all()

    return [
        {
            "timestamp": s.timestamp.isoformat(),
            "total_value": s.total_value,
            "cash": s.cash,
            "total_pnl": s.total_pnl,
            "total_pnl_percentage": s.total_pnl_percentage,
            "win_rate": s.win_rate,
            "total_trades": s.total_trades
        }
        for s in reversed(snapshots)
    ]


@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall statistics."""
    from sqlalchemy import func
    from app.models.trade import TradeStatus

    total_trades = db.query(Trade).filter(Trade.status == TradeStatus.CLOSED).count()
    winning_trades = db.query(Trade).filter(
        Trade.status == TradeStatus.CLOSED,
        Trade.pnl > 0
    ).count()

    total_pnl = db.query(func.sum(Trade.pnl)).filter(
        Trade.status == TradeStatus.CLOSED
    ).scalar() or 0

    avg_pnl = db.query(func.avg(Trade.pnl)).filter(
        Trade.status == TradeStatus.CLOSED
    ).scalar() or 0

    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": total_trades - winning_trades,
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl": round(avg_pnl, 2)
    }
