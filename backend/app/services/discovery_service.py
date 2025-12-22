"""
Discovery Service - Découvre et gère les opportunités de trading
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models.watchlist import Watchlist, WatchlistPriority, WatchlistStatus
import logging

logger = logging.getLogger(__name__)


class DiscoveryService:
    """Service pour découvrir et gérer les opportunités de trading"""

    def __init__(self, db: Session):
        self.db = db

    def add_to_watchlist(
        self,
        symbol: str,
        score: float,
        reason: str,
        sources: Optional[Dict[str, Any]] = None,
        priority: WatchlistPriority = WatchlistPriority.MEDIUM,
    ) -> Watchlist:
        """Ajoute un symbole à la watchlist"""
        # Vérifie si le symbole existe déjà dans la watchlist active
        existing = (
            self.db.query(Watchlist)
            .filter(
                Watchlist.symbol == symbol,
                Watchlist.status.in_([WatchlistStatus.WATCHING, WatchlistStatus.ANALYZING]),
            )
            .first()
        )

        if existing:
            # Met à jour le score et la raison si le nouveau score est meilleur
            if score > existing.score:
                existing.score = score
                existing.reason = reason
                existing.sources = sources or existing.sources
                existing.priority = priority
                existing.last_analyzed = datetime.now()
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Watchlist mise à jour: {symbol} (score: {score})")
                return existing
            else:
                logger.info(f"Symbole {symbol} déjà en watchlist avec un meilleur score")
                return existing

        # Crée une nouvelle entrée
        watchlist_item = Watchlist(
            symbol=symbol,
            score=score,
            reason=reason,
            sources=sources or {},
            priority=priority,
            status=WatchlistStatus.WATCHING,
        )

        self.db.add(watchlist_item)
        self.db.commit()
        self.db.refresh(watchlist_item)

        logger.info(f"Nouvelle opportunité ajoutée à la watchlist: {symbol} (score: {score})")
        return watchlist_item

    def get_watchlist(
        self, status: Optional[WatchlistStatus] = None, min_score: float = 0.0
    ) -> List[Watchlist]:
        """Récupère la watchlist, optionnellement filtrée par statut et score minimum"""
        query = self.db.query(Watchlist).filter(Watchlist.score >= min_score)

        if status:
            query = query.filter(Watchlist.status == status)
        else:
            # Par défaut, ne retourne que les items actifs
            query = query.filter(
                Watchlist.status.in_([WatchlistStatus.WATCHING, WatchlistStatus.ANALYZING])
            )

        return query.order_by(Watchlist.score.desc(), Watchlist.priority.desc()).all()

    def get_watchlist_item(self, watchlist_id: int) -> Optional[Watchlist]:
        """Récupère un item de watchlist par ID"""
        return self.db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()

    def get_watchlist_by_symbol(self, symbol: str) -> Optional[Watchlist]:
        """Récupère un item de watchlist par symbole (actif uniquement)"""
        return (
            self.db.query(Watchlist)
            .filter(
                Watchlist.symbol == symbol,
                Watchlist.status.in_([WatchlistStatus.WATCHING, WatchlistStatus.ANALYZING]),
            )
            .first()
        )

    def update_watchlist_status(
        self, watchlist_id: int, status: WatchlistStatus
    ) -> Optional[Watchlist]:
        """Met à jour le statut d'un item de watchlist"""
        item = self.get_watchlist_item(watchlist_id)
        if not item:
            return None

        item.status = status
        item.last_analyzed = datetime.now()
        self.db.commit()
        self.db.refresh(item)

        logger.info(f"Watchlist {item.symbol} statut mis à jour: {status.value}")
        return item

    def update_watchlist_score(
        self, watchlist_id: int, new_score: float, reason: Optional[str] = None
    ) -> Optional[Watchlist]:
        """Met à jour le score d'un item de watchlist"""
        item = self.get_watchlist_item(watchlist_id)
        if not item:
            return None

        item.score = new_score
        if reason:
            item.reason = reason
        item.last_analyzed = datetime.now()
        self.db.commit()
        self.db.refresh(item)

        logger.info(f"Score watchlist {item.symbol} mis à jour: {new_score}")
        return item

    def mark_as_traded(self, watchlist_id: int) -> Optional[Watchlist]:
        """Marque un item comme tradé"""
        return self.update_watchlist_status(watchlist_id, WatchlistStatus.TRADED)

    def remove_from_watchlist(self, watchlist_id: int) -> Optional[Watchlist]:
        """Retire un item de la watchlist (status REMOVED)"""
        return self.update_watchlist_status(watchlist_id, WatchlistStatus.REMOVED)

    def cleanup_old_items(self, days: int = 7) -> int:
        """
        Nettoie les items anciens de la watchlist
        Retire les items avec status WATCHING qui n'ont pas été analysés depuis X jours
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        items_to_remove = (
            self.db.query(Watchlist)
            .filter(
                Watchlist.status == WatchlistStatus.WATCHING,
                Watchlist.priority == WatchlistPriority.LOW,
                Watchlist.last_analyzed < cutoff_date,
            )
            .all()
        )

        count = 0
        for item in items_to_remove:
            item.status = WatchlistStatus.REMOVED
            count += 1

        self.db.commit()

        if count > 0:
            logger.info(f"{count} items retirés de la watchlist (nettoyage automatique)")

        return count

    def get_top_opportunities(self, limit: int = 10) -> List[Watchlist]:
        """Récupère les meilleures opportunités (score le plus élevé)"""
        return (
            self.db.query(Watchlist)
            .filter(
                Watchlist.status.in_([WatchlistStatus.WATCHING, WatchlistStatus.ANALYZING])
            )
            .order_by(Watchlist.score.desc())
            .limit(limit)
            .all()
        )

    def get_watchlist_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la watchlist"""
        total = self.db.query(Watchlist).count()
        watching = (
            self.db.query(Watchlist)
            .filter(Watchlist.status == WatchlistStatus.WATCHING)
            .count()
        )
        analyzing = (
            self.db.query(Watchlist)
            .filter(Watchlist.status == WatchlistStatus.ANALYZING)
            .count()
        )
        traded = (
            self.db.query(Watchlist)
            .filter(Watchlist.status == WatchlistStatus.TRADED)
            .count()
        )
        removed = (
            self.db.query(Watchlist)
            .filter(Watchlist.status == WatchlistStatus.REMOVED)
            .count()
        )

        avg_score = self.db.query(Watchlist).filter(
            Watchlist.status.in_([WatchlistStatus.WATCHING, WatchlistStatus.ANALYZING])
        )
        avg_score_value = 0.0
        if avg_score.count() > 0:
            avg_score_value = sum(item.score for item in avg_score.all()) / avg_score.count()

        return {
            "total": total,
            "watching": watching,
            "analyzing": analyzing,
            "traded": traded,
            "removed": removed,
            "average_score": round(avg_score_value, 2),
        }
