from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # General
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # API Keys
    XAI_API_KEY: str  # Clé API xAI pour Grok
    GROK_MODEL: str = "grok-2-1212"  # Modèle par défaut

    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    GOOGLE_SEARCH_API_KEY: str = ""
    GOOGLE_SEARCH_ENGINE_ID: str = ""
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""

    # Trading
    TRADING_MODE: str = "paper"
    INITIAL_CAPITAL: float = 10000.0
    WATCHED_SYMBOLS: str = "BTC/USDT,ETH/USDT,AAPL,TSLA"

    MAX_POSITIONS: int = 3
    MAX_POSITION_SIZE_PCT: float = 20.0

    STOP_LOSS_DEFAULT: float = 5.0
    TAKE_PROFIT_DEFAULT: float = 10.0
    MAX_DRAWDOWN: float = 20.0
    MAX_DAILY_LOSS_PCT: float = 10.0

    MAX_TRADES_PER_DAY: int = 5
    MIN_INTERVAL_BETWEEN_TRADES: int = 3600

    REFLECTION_INTERVAL: int = 5
    REFLECTION_ENABLED: bool = True

    # Autonomous Trading Cycles
    DISCOVERY_INTERVAL: int = 3600  # 1 hour
    ANALYSIS_INTERVAL: int = 1800  # 30 minutes
    MONITORING_INTERVAL: int = 900  # 15 minutes
    REFLECTION_TRADES_THRESHOLD: int = 10

    # Strategy
    AUTO_STRATEGY_CREATION: bool = True
    STRATEGY_RISK_PROFILE: str = "moderate"  # conservative, moderate, aggressive

    # Watchlist
    MAX_WATCHLIST_SIZE: int = 20
    MIN_OPPORTUNITY_SCORE: float = 6.0
    AUTO_REMOVE_LOW_PRIORITY_DAYS: int = 7

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    TIMEOUT: int = 120

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/tmp/trading-ai-backend.log"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def watched_symbols_list(self) -> List[str]:
        return [symbol.strip() for symbol in self.WATCHED_SYMBOLS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
