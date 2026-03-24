"""Trading strategies for backtesting."""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict

from utils.logger import get_logger

logger = get_logger(__name__)


class BaseStrategy(ABC):
    """Base class for trading strategies."""
    
    def __init__(self, name: str, params: Dict = None):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
        """
        self.name = name
        self.params = params or {}
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with features
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.name}({self.params})"


class RSIStrategy(BaseStrategy):
    """RSI mean reversion strategy."""
    
    def __init__(self, buy_threshold: float = 30, sell_threshold: float = 70):
        """
        Initialize RSI strategy.
        
        Args:
            buy_threshold: RSI level to buy (oversold)
            sell_threshold: RSI level to sell (overbought)
        """
        params = {
            'buy_threshold': buy_threshold,
            'sell_threshold': sell_threshold
        }
        super().__init__("RSI Strategy", params)
        
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate RSI-based signals."""
        if 'rsi' not in df.columns:
            logger.error("RSI column not found in DataFrame")
            return pd.Series(0, index=df.index)
        
        signals = pd.Series(0, index=df.index)
        
        # Buy when RSI < buy_threshold (oversold)
        signals[df['rsi'] < self.buy_threshold] = 1
        
        # Sell when RSI > sell_threshold (overbought)
        signals[df['rsi'] > self.sell_threshold] = -1
        
        return signals


class MACDStrategy(BaseStrategy):
    """MACD crossover strategy."""
    
    def __init__(self):
        """Initialize MACD strategy."""
        super().__init__("MACD Strategy", {})
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate MACD crossover signals."""
        if 'macd' not in df.columns or 'macd_signal' not in df.columns:
            logger.error("MACD columns not found in DataFrame")
            return pd.Series(0, index=df.index)
        
        signals = pd.Series(0, index=df.index)
        
        # Calculate crossovers
        macd_diff = df['macd'] - df['macd_signal']
        macd_diff_prev = macd_diff.shift(1)
        
        # Buy when MACD crosses above signal
        signals[(macd_diff > 0) & (macd_diff_prev <= 0)] = 1
        
        # Sell when MACD crosses below signal
        signals[(macd_diff < 0) & (macd_diff_prev >= 0)] = -1
        
        return signals


class TrendFollowingStrategy(BaseStrategy):
    """Trend following strategy using moving averages."""
    
    def __init__(self, ma_period: int = 50, momentum_threshold: float = 0):
        """
        Initialize trend following strategy.
        
        Args:
            ma_period: Moving average period
            momentum_threshold: Momentum threshold for entry
        """
        params = {
            'ma_period': ma_period,
            'momentum_threshold': momentum_threshold
        }
        super().__init__("Trend Following Strategy", params)
        
        self.ma_period = ma_period
        self.momentum_threshold = momentum_threshold
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate trend following signals."""
        ma_col = f'sma_{self.ma_period}'
        
        if ma_col not in df.columns or 'close' not in df.columns:
            logger.error(f"Required columns not found: {ma_col}, close")
            return pd.Series(0, index=df.index)
        
        signals = pd.Series(0, index=df.index)
        
        # Check if momentum score exists
        if 'momentum_score' in df.columns:
            # Buy when price > MA and momentum positive
            buy_condition = (df['close'] > df[ma_col]) & (df['momentum_score'] > self.momentum_threshold)
            signals[buy_condition] = 1
            
            # Sell when price < MA
            sell_condition = df['close'] < df[ma_col]
            signals[sell_condition] = -1
        else:
            # Simple version without momentum
            signals[df['close'] > df[ma_col]] = 1
            signals[df['close'] < df[ma_col]] = -1
        
        return signals


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands mean reversion strategy."""
    
    def __init__(self):
        """Initialize Bollinger Bands strategy."""
        super().__init__("Bollinger Bands Strategy", {})
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate Bollinger Bands signals."""
        required_cols = ['close', 'bb_lower', 'bb_upper']
        
        if not all(col in df.columns for col in required_cols):
            logger.error("Bollinger Bands columns not found")
            return pd.Series(0, index=df.index)
        
        signals = pd.Series(0, index=df.index)
        
        # Buy when price touches lower band
        signals[df['close'] <= df['bb_lower']] = 1
        
        # Sell when price touches upper band
        signals[df['close'] >= df['bb_upper']] = -1
        
        return signals
