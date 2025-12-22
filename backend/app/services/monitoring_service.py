"""
Monitoring Service - Surveille les positions et les événements de marché
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models.market_event import MarketEvent, EventType, EventSeverity, ActionTaken
from app.models.trade import Trade, TradeStatus
import logging

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service pour surveiller les positions et les événements de marché"""

    def __init__(self, db: Session):
        self.db = db

    def create_event(
        self,
        symbol: str,
        event_type: EventType,
        severity: EventSeverity,
        description: str,
        source: str,
        impact_assessment: Optional[str] = None,
        action_taken: ActionTaken = ActionTaken.NONE,
        related_trade_id: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> MarketEvent:
        """Crée un nouvel événement de marché"""
        event = MarketEvent(
            symbol=symbol,
            event_type=event_type,
            severity=severity,
            description=description,
            source=source,
            impact_assessment=impact_assessment,
            action_taken=action_taken,
            related_trade_id=related_trade_id,
            extra_data=extra_data or {},
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        logger.info(
            f"Événement de marché créé: {symbol} - {event_type.value} ({severity.value})"
        )
        return event

    def get_events(
        self,
        symbol: Optional[str] = None,
        event_type: Optional[EventType] = None,
        severity: Optional[EventSeverity] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[MarketEvent]:
        """Récupère les événements de marché avec filtres optionnels"""
        query = self.db.query(MarketEvent)

        if symbol:
            query = query.filter(MarketEvent.symbol == symbol)
        if event_type:
            query = query.filter(MarketEvent.event_type == event_type)
        if severity:
            query = query.filter(MarketEvent.severity == severity)
        if since:
            query = query.filter(MarketEvent.timestamp >= since)

        return query.order_by(MarketEvent.timestamp.desc()).limit(limit).all()

    def get_event_by_id(self, event_id: int) -> Optional[MarketEvent]:
        """Récupère un événement par ID"""
        return self.db.query(MarketEvent).filter(MarketEvent.id == event_id).first()

    def get_recent_events(self, hours: int = 24, limit: int = 50) -> List[MarketEvent]:
        """Récupère les événements récents"""
        since = datetime.now() - timedelta(hours=hours)
        return self.get_events(since=since, limit=limit)

    def get_events_for_trade(self, trade_id: int) -> List[MarketEvent]:
        """Récupère tous les événements liés à un trade"""
        return (
            self.db.query(MarketEvent)
            .filter(MarketEvent.related_trade_id == trade_id)
            .order_by(MarketEvent.timestamp.desc())
            .all()
        )

    def get_critical_events(self, hours: int = 24) -> List[MarketEvent]:
        """Récupère les événements critiques récents"""
        since = datetime.now() - timedelta(hours=hours)
        return (
            self.db.query(MarketEvent)
            .filter(
                MarketEvent.severity == EventSeverity.CRITICAL, MarketEvent.timestamp >= since
            )
            .order_by(MarketEvent.timestamp.desc())
            .all()
        )

    def update_event_action(
        self, event_id: int, action_taken: ActionTaken, impact_assessment: Optional[str] = None
    ) -> Optional[MarketEvent]:
        """Met à jour l'action prise pour un événement"""
        event = self.get_event_by_id(event_id)
        if not event:
            return None

        event.action_taken = action_taken
        if impact_assessment:
            event.impact_assessment = impact_assessment

        self.db.commit()
        self.db.refresh(event)

        logger.info(f"Action mise à jour pour événement {event_id}: {action_taken.value}")
        return event

    def check_position_alerts(self, trade: Trade, current_price: float) -> List[Dict[str, Any]]:
        """
        Vérifie si des alertes doivent être déclenchées pour une position
        Retourne une liste d'alertes
        """
        alerts = []

        if trade.status != TradeStatus.OPEN:
            return alerts

        # Calcul du P&L actuel
        pnl_percentage = ((current_price - trade.entry_price) / trade.entry_price) * 100

        # Vérification stop-loss
        if trade.stop_loss and current_price <= trade.stop_loss:
            alerts.append({
                "type": "stop_loss_hit",
                "severity": EventSeverity.HIGH,
                "message": f"Stop-loss atteint pour {trade.symbol} @ {current_price}",
                "recommended_action": ActionTaken.EXIT_FULL,
                "details": {
                    "entry_price": trade.entry_price,
                    "current_price": current_price,
                    "stop_loss": trade.stop_loss,
                    "pnl_percentage": round(pnl_percentage, 2),
                },
            })

        # Vérification take-profit
        if trade.take_profit and current_price >= trade.take_profit:
            alerts.append({
                "type": "take_profit_hit",
                "severity": EventSeverity.MEDIUM,
                "message": f"Take-profit atteint pour {trade.symbol} @ {current_price}",
                "recommended_action": ActionTaken.TAKE_PROFIT,
                "details": {
                    "entry_price": trade.entry_price,
                    "current_price": current_price,
                    "take_profit": trade.take_profit,
                    "pnl_percentage": round(pnl_percentage, 2),
                },
            })

        # Vérification gains importants (> 20%)
        if pnl_percentage > 20:
            alerts.append({
                "type": "significant_gain",
                "severity": EventSeverity.LOW,
                "message": f"Gain important pour {trade.symbol}: +{pnl_percentage:.2f}%",
                "recommended_action": ActionTaken.EXIT_PARTIAL,
                "details": {
                    "entry_price": trade.entry_price,
                    "current_price": current_price,
                    "pnl_percentage": round(pnl_percentage, 2),
                },
            })

        # Vérification pertes importantes (> 10% sans stop-loss)
        if pnl_percentage < -10 and not trade.stop_loss:
            alerts.append({
                "type": "significant_loss",
                "severity": EventSeverity.HIGH,
                "message": f"Perte importante pour {trade.symbol}: {pnl_percentage:.2f}%",
                "recommended_action": ActionTaken.ADJUST_STOP,
                "details": {
                    "entry_price": trade.entry_price,
                    "current_price": current_price,
                    "pnl_percentage": round(pnl_percentage, 2),
                },
            })

        return alerts

    def get_event_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Retourne des statistiques sur les événements"""
        since = datetime.now() - timedelta(days=days)

        total = self.db.query(MarketEvent).filter(MarketEvent.timestamp >= since).count()

        by_type = {}
        for event_type in EventType:
            count = (
                self.db.query(MarketEvent)
                .filter(
                    MarketEvent.timestamp >= since, MarketEvent.event_type == event_type
                )
                .count()
            )
            if count > 0:
                by_type[event_type.value] = count

        by_severity = {}
        for severity in EventSeverity:
            count = (
                self.db.query(MarketEvent)
                .filter(
                    MarketEvent.timestamp >= since, MarketEvent.severity == severity
                )
                .count()
            )
            if count > 0:
                by_severity[severity.value] = count

        return {
            "total_events": total,
            "period_days": days,
            "by_type": by_type,
            "by_severity": by_severity,
        }
