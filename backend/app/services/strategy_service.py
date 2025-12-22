"""
Strategy Service - Gère les stratégies de trading
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.trading_strategy import TradingStrategy
from app.models.strategy_adjustment import StrategyAdjustment, AdjustmentType, AdjustmentCreator
import logging

logger = logging.getLogger(__name__)


class StrategyService:
    """Service pour gérer les stratégies de trading"""

    def __init__(self, db: Session):
        self.db = db

    def get_active_strategy(self) -> Optional[TradingStrategy]:
        """Récupère la stratégie active"""
        return (
            self.db.query(TradingStrategy)
            .filter(TradingStrategy.is_active == True)
            .order_by(TradingStrategy.created_at.desc())
            .first()
        )

    def get_strategy_by_id(self, strategy_id: int) -> Optional[TradingStrategy]:
        """Récupère une stratégie par son ID"""
        return self.db.query(TradingStrategy).filter(TradingStrategy.id == strategy_id).first()

    def create_strategy(
        self,
        style: str,
        description: str,
        entry_criteria: Dict[str, Any],
        exit_criteria: Dict[str, Any],
        risk_management: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> TradingStrategy:
        """Crée une nouvelle stratégie"""
        # Désactive les anciennes stratégies
        self.db.query(TradingStrategy).update({"is_active": False})

        # Calcule le numéro de version
        max_version = self.db.query(TradingStrategy).count()

        # Crée la nouvelle stratégie
        strategy = TradingStrategy(
            version=max_version + 1,
            style=style,
            description=description,
            entry_criteria=entry_criteria,
            exit_criteria=exit_criteria,
            risk_management=risk_management,
            parameters=parameters or {},
            is_active=True,
            performance_metrics={},
        )

        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)

        logger.info(f"Nouvelle stratégie créée: v{strategy.version} - {strategy.style}")
        return strategy

    def update_strategy_performance(
        self, strategy_id: int, metrics: Dict[str, Any]
    ) -> Optional[TradingStrategy]:
        """Met à jour les métriques de performance d'une stratégie"""
        strategy = self.get_strategy_by_id(strategy_id)
        if not strategy:
            return None

        strategy.performance_metrics = metrics
        self.db.commit()
        self.db.refresh(strategy)

        logger.info(f"Métriques de performance mises à jour pour stratégie {strategy_id}")
        return strategy

    def adjust_strategy(
        self,
        strategy_id: int,
        adjustment_type: AdjustmentType,
        reason: str,
        changes: Dict[str, Any],
        created_by: AdjustmentCreator,
        performance_before: Optional[Dict[str, Any]] = None,
    ) -> StrategyAdjustment:
        """Enregistre un ajustement de stratégie"""
        adjustment = StrategyAdjustment(
            strategy_id=strategy_id,
            adjustment_type=adjustment_type,
            created_by=created_by,
            reason=reason,
            changes=changes,
            performance_before=performance_before,
        )

        self.db.add(adjustment)
        self.db.commit()
        self.db.refresh(adjustment)

        logger.info(
            f"Ajustement enregistré pour stratégie {strategy_id}: {adjustment_type.value}"
        )
        return adjustment

    def get_strategy_adjustments(self, strategy_id: int) -> list[StrategyAdjustment]:
        """Récupère tous les ajustements d'une stratégie"""
        return (
            self.db.query(StrategyAdjustment)
            .filter(StrategyAdjustment.strategy_id == strategy_id)
            .order_by(StrategyAdjustment.timestamp.desc())
            .all()
        )

    def apply_adjustment(
        self,
        strategy_id: int,
        adjustment: StrategyAdjustment,
        create_new_version: bool = False,
    ) -> TradingStrategy:
        """
        Applique un ajustement à une stratégie
        Si create_new_version=True, crée une nouvelle version de la stratégie
        Sinon, modifie la stratégie existante
        """
        current_strategy = self.get_strategy_by_id(strategy_id)
        if not current_strategy:
            raise ValueError(f"Stratégie {strategy_id} introuvable")

        changes = adjustment.changes

        if create_new_version:
            # Crée une nouvelle version
            new_strategy = TradingStrategy(
                version=current_strategy.version + 1,
                style=changes.get("style", current_strategy.style),
                description=changes.get("description", current_strategy.description),
                entry_criteria=changes.get("entry_criteria", current_strategy.entry_criteria),
                exit_criteria=changes.get("exit_criteria", current_strategy.exit_criteria),
                risk_management=changes.get(
                    "risk_management", current_strategy.risk_management
                ),
                parameters=changes.get("parameters", current_strategy.parameters),
                is_active=True,
                performance_metrics={},
            )

            # Désactive l'ancienne
            current_strategy.is_active = False

            self.db.add(new_strategy)
            self.db.commit()
            self.db.refresh(new_strategy)

            logger.info(
                f"Nouvelle version de stratégie créée: v{new_strategy.version} (ajustement {adjustment.id})"
            )
            return new_strategy
        else:
            # Modifie la stratégie existante
            if "style" in changes:
                current_strategy.style = changes["style"]
            if "description" in changes:
                current_strategy.description = changes["description"]
            if "entry_criteria" in changes:
                current_strategy.entry_criteria = changes["entry_criteria"]
            if "exit_criteria" in changes:
                current_strategy.exit_criteria = changes["exit_criteria"]
            if "risk_management" in changes:
                current_strategy.risk_management = changes["risk_management"]
            if "parameters" in changes:
                current_strategy.parameters = changes["parameters"]

            self.db.commit()
            self.db.refresh(current_strategy)

            logger.info(
                f"Stratégie {strategy_id} mise à jour (ajustement {adjustment.id})"
            )
            return current_strategy
