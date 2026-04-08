"""Core feature engineering logic for financial time-series data."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import ta

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    """Compute financial features from OHLCV data."""
    
    def __init__(self):
        """Initialize feature engineer with configuration."""
        # Window sizes
        self.window_short = config.get('features.windows.short', 10)
        self.window_medium = config.get('features.windows.medium', 30)
        self.window_long = config.get('features.windows.long', 50)
        self.window_volatility = config.get('features.windows.volatility', 20)
        
        # Technical indicator parameters
        self.rsi_period = config.get('features.indicators.rsi_period', 14)
        self.macd_fast = config.get('features.indicators.macd_fast', 12)
        self.macd_slow = config.get('features.indicators.macd_slow', 26)
        self.macd_signal = config.get('features.indicators.macd_signal', 9)
        self.bollinger_std = config.get('features.indicators.bollinger_std', 2)
        self.atr_period = config.get('features.indicators.atr_period', 14)
        
        # Lag features
        self.price_lags = config.get('features.lags.price_lags', [1, 5, 10])
        self.volume_lags = config.get('features.lags.volume_lags', [1, 5])
        
        logger.info("FeatureEngineer initialized")
    
    def compute_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all features for the dataset.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all features
        """
        logger.info("Computing all features...")
        
        # Ensure data is sorted
        df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
        
        # Process each ticker separately
        result_dfs = []
        for ticker in df['ticker'].unique():
            ticker_df = df[df['ticker'] == ticker].copy()
            ticker_df = self._compute_ticker_features(ticker_df)
            result_dfs.append(ticker_df)
        
        result = pd.concat(result_dfs, ignore_index=True)
        logger.info(f"Feature engineering complete. Total features: {len(result.columns)}")
        
        return result
    
    def _compute_ticker_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute features for a single ticker."""
        # Basic features
        df = self._compute_basic_features(df)
        
        # Trend features
        df = self._compute_trend_features(df)
        
        # Volatility features
        df = self._compute_volatility_features(df)
        
        # Momentum features
        df = self._compute_momentum_features(df)
        
        # Lag features
        df = self._compute_lag_features(df)
        
        # Advanced features
        df = self._compute_advanced_features(df)
        
        return df
    
    def _compute_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute basic price and return features."""
        # Daily returns
        df['return'] = df['close'].pct_change()
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # Intraday range
        df['high_low_range'] = (df['high'] - df['low']) / df['close']
        df['open_close_range'] = (df['close'] - df['open']) / df['open']
        
        # Volume change
        df['volume_change'] = df['volume'].pct_change()
        
        return df
    
    def _compute_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute trend-based features."""
        # Moving averages
        df[f'sma_{self.window_short}'] = df['close'].rolling(window=self.window_short).mean()
        df[f'sma_{self.window_medium}'] = df['close'].rolling(window=self.window_medium).mean()
        df[f'sma_{self.window_long}'] = df['close'].rolling(window=self.window_long).mean()
        
        # Exponential moving averages
        df[f'ema_{self.window_short}'] = df['close'].ewm(span=self.window_short, adjust=False).mean()
        df[f'ema_{self.window_medium}'] = df['close'].ewm(span=self.window_medium, adjust=False).mean()
        
        # Price relative to moving averages
        df[f'price_to_sma_{self.window_short}'] = df['close'] / df[f'sma_{self.window_short}'] - 1
        df[f'price_to_sma_{self.window_medium}'] = df['close'] / df[f'sma_{self.window_medium}'] - 1
        df[f'price_to_sma_{self.window_long}'] = df['close'] / df[f'sma_{self.window_long}'] - 1
        
        # Trend slope (linear regression)
        df[f'trend_slope_{self.window_short}'] = self._calculate_trend_slope(df['close'], self.window_short)
        df[f'trend_slope_{self.window_medium}'] = self._calculate_trend_slope(df['close'], self.window_medium)
        
        return df
    
    def _compute_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute volatility-based features."""
        # Rolling standard deviation
        df[f'volatility_{self.window_short}'] = df['return'].rolling(window=self.window_short).std()
        df[f'volatility_{self.window_medium}'] = df['return'].rolling(window=self.window_medium).std()
        
        # Average True Range (ATR)
        df['atr'] = ta.volatility.average_true_range(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.atr_period
        )
        df['atr_pct'] = df['atr'] / df['close']
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(
            close=df['close'],
            window=self.window_volatility,
            window_dev=self.bollinger_std
        )
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        df['bb_lower'] = bollinger.bollinger_lband()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def _compute_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute momentum-based features."""
        # RSI
        df['rsi'] = ta.momentum.rsi(df['close'], window=self.rsi_period)
        
        # MACD
        macd = ta.trend.MACD(
            close=df['close'],
            window_fast=self.macd_fast,
            window_slow=self.macd_slow,
            window_sign=self.macd_signal
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14,
            smooth_window=3
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        # Rate of Change (ROC)
        df['roc_10'] = ta.momentum.roc(df['close'], window=10)
        df['roc_30'] = ta.momentum.roc(df['close'], window=30)
        
        # Money Flow Index
        df['mfi'] = ta.volume.money_flow_index(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume'],
            window=14
        )
        
        return df
    
    def _compute_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute lag features."""
        # Price lags
        for lag in self.price_lags:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'return_lag_{lag}'] = df['return'].shift(lag)
        
        # Volume lags
        for lag in self.volume_lags:
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
        
        # ENHANCEMENT: Additional short-term lags (1, 2, 3 days) for better prediction
        for lag in [1, 2, 3]:
            if f'return_lag_{lag}' not in df.columns:
                df[f'return_lag_{lag}'] = df['return'].shift(lag)
            if f'volume_change_lag_{lag}' not in df.columns:
                df[f'volume_change_lag_{lag}'] = df['volume'].pct_change().shift(lag)
        
        return df
    
    def _compute_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute advanced composite features."""
        # Regime detection
        df['regime'] = self._detect_regime(df)
        
        # Momentum score (composite)
        df['momentum_score'] = self._calculate_momentum_score(df)
        
        # Feature interactions
        if 'volatility_10' in df.columns and 'return' in df.columns:
            df['volatility_return_interaction'] = df['volatility_10'] * df['return']
        
        if 'volume_change' in df.columns and 'return' in df.columns:
            df['volume_price_interaction'] = df['volume_change'] * df['return']
        
        # Price momentum
        df['price_momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['price_momentum_20'] = df['close'] / df['close'].shift(20) - 1
        
        # Volume momentum
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_to_sma'] = df['volume'] / df['volume_sma_20']
        
        # ENHANCEMENT: Rolling statistics for recent trends
        for window in [3, 5, 7]:
            df[f'return_mean_{window}d'] = df['return'].rolling(window).mean()
            df[f'return_std_{window}d'] = df['return'].rolling(window).std()
        
        # ENHANCEMENT: Acceleration features (rate of change of change)
        df['price_acceleration'] = df['return'] - df['return'].shift(1)
        df['volume_acceleration'] = df['volume'].pct_change() - df['volume'].pct_change().shift(1)
        
        # ENHANCEMENT: RSI momentum and divergence
        if 'rsi' in df.columns:
            df['rsi_momentum'] = df['rsi'].diff()
            df['rsi_divergence'] = df['rsi'] - df['rsi'].rolling(10).mean()
        
        # ENHANCEMENT: MACD strength and trend
        if 'macd_diff' in df.columns:
            df['macd_strength'] = df['macd_diff'].abs()
            df['macd_trend'] = (df['macd_diff'] > 0).astype(int).rolling(5).mean()
        
        # ENHANCEMENT: Price position in recent range
        high_20 = df['high'].rolling(20).max()
        low_20 = df['low'].rolling(20).min()
        df['price_position_20d'] = (df['close'] - low_20) / (high_20 - low_20 + 1e-10)
        
        return df
    
    def _calculate_trend_slope(self, series: pd.Series, window: int) -> pd.Series:
        """Calculate rolling linear regression slope."""
        def slope(y):
            if len(y) < 2:
                return np.nan
            x = np.arange(len(y))
            return np.polyfit(x, y, 1)[0]
        
        return series.rolling(window=window).apply(slope, raw=False)
    
    def _detect_regime(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect market regime (bull/bear/sideways).
        
        Returns:
            Series with regime labels: 1 (bull), 0 (sideways), -1 (bear)
        """
        threshold = config.get('features.regime.trend_threshold', 0.02)
        
        if f'trend_slope_{self.window_medium}' not in df.columns:
            return pd.Series(0, index=df.index)
        
        slope = df[f'trend_slope_{self.window_medium}']
        
        regime = pd.Series(0, index=df.index)  # Default: sideways
        regime[slope > threshold] = 1  # Bull
        regime[slope < -threshold] = -1  # Bear
        
        return regime
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate composite momentum score.
        
        Combines multiple momentum indicators into a single score.
        """
        score = pd.Series(0.0, index=df.index)
        count = 0
        
        # RSI component (normalized to -1 to 1)
        if 'rsi' in df.columns:
            rsi_norm = (df['rsi'] - 50) / 50
            score += rsi_norm
            count += 1
        
        # MACD component
        if 'macd_diff' in df.columns:
            macd_norm = np.tanh(df['macd_diff'])  # Normalize using tanh
            score += macd_norm
            count += 1
        
        # Price momentum component
        if 'price_momentum_20' in df.columns:
            price_mom_norm = np.tanh(df['price_momentum_20'] * 10)
            score += price_mom_norm
            count += 1
        
        # Average the components
        if count > 0:
            score = score / count
        
        return score
    
    def get_feature_metadata(self) -> Dict[str, Dict]:
        """
        Get metadata for all features.
        
        Returns:
            Dictionary with feature metadata
        """
        metadata = {
            'return': {
                'description': 'Daily simple return',
                'formula': '(close_t - close_t-1) / close_t-1'
            },
            'log_return': {
                'description': 'Daily log return',
                'formula': 'log(close_t / close_t-1)'
            },
            f'sma_{self.window_short}': {
                'description': f'{self.window_short}-day simple moving average',
                'formula': f'mean(close, {self.window_short})'
            },
            'rsi': {
                'description': f'{self.rsi_period}-period Relative Strength Index',
                'formula': '100 - (100 / (1 + RS))'
            },
            'macd': {
                'description': 'MACD line',
                'formula': f'EMA({self.macd_fast}) - EMA({self.macd_slow})'
            },
            'atr': {
                'description': f'{self.atr_period}-period Average True Range',
                'formula': 'EMA(TR, period)'
            },
            'regime': {
                'description': 'Market regime classification',
                'formula': '1 (bull), 0 (sideways), -1 (bear)'
            },
            'momentum_score': {
                'description': 'Composite momentum indicator',
                'formula': 'Average of normalized RSI, MACD, and price momentum'
            }
        }
        
        return metadata


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to compute features.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with computed features
    """
    engineer = FeatureEngineer()
    return engineer.compute_all_features(df)
