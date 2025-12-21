import yfinance as yf
import ccxt
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime, timedelta


class MarketDataService:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.cache = {}
        self.cache_duration = 60  # seconds

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol (crypto or stock)."""
        try:
            if self._is_crypto(symbol):
                ticker = self.exchange.fetch_ticker(symbol)
                return ticker['last']
            else:
                # Stock
                stock = yf.Ticker(symbol)
                data = stock.history(period='1d', interval='1m')
                if not data.empty:
                    return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Calculate technical indicators for a symbol."""
        try:
            # Get historical data
            if self._is_crypto(symbol):
                ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            else:
                stock = yf.Ticker(symbol)
                df = stock.history(period='1mo', interval='1h')
                df = df.reset_index()
                df.columns = [c.lower() for c in df.columns]

            if df.empty:
                return {}

            # Calculate indicators
            close = df['close']

            # RSI
            rsi = self._calculate_rsi(close)

            # MACD
            macd, signal, histogram = self._calculate_macd(close)

            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close)

            # Volume analysis
            avg_volume = df['volume'].mean()
            current_volume = df['volume'].iloc[-1]

            # Price momentum
            price_change_24h = ((close.iloc[-1] - close.iloc[-24]) / close.iloc[-24] * 100) if len(close) >= 24 else 0

            return {
                "rsi": round(rsi, 2),
                "macd": {
                    "macd": round(macd, 4),
                    "signal": round(signal, 4),
                    "histogram": round(histogram, 4)
                },
                "bollinger_bands": {
                    "upper": round(bb_upper, 2),
                    "middle": round(bb_middle, 2),
                    "lower": round(bb_lower, 2)
                },
                "volume": {
                    "current": int(current_volume),
                    "average": int(avg_volume),
                    "ratio": round(current_volume / avg_volume, 2) if avg_volume > 0 else 0
                },
                "momentum": {
                    "price_change_24h": round(price_change_24h, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def _calculate_macd(self, prices: pd.Series, fast=12, slow=26, signal=9):
        """Calculate MACD indicator."""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]

    def _calculate_bollinger_bands(self, prices: pd.Series, period=20, std_dev=2):
        """Calculate Bollinger Bands."""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper.iloc[-1], middle.iloc[-1], lower.iloc[-1]

    def _is_crypto(self, symbol: str) -> bool:
        """Check if symbol is crypto (contains /)."""
        return '/' in symbol

    def get_market_overview(self, symbols: list) -> Dict[str, Dict]:
        """Get overview of multiple symbols."""
        overview = {}
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                overview[symbol] = {
                    "price": price,
                    "type": "crypto" if self._is_crypto(symbol) else "stock"
                }
        return overview


market_data_service = MarketDataService()
