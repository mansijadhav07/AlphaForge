"""
Data Service Layer for AlphaForge.

Provides centralized access to:
- Raw market data (yfinance)
- Engineered features (feature store)
- PGM predictions and explanations
- Cached results

NO MOCK DATA - All functions return real data or raise exceptions.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import json

from data.features.offline_store import OfflineFeatureStore
from data.ingestion.ingestion import DataIngestion
from utils.logger import get_logger

logger = get_logger(__name__)


class DataService:
    """
    Centralized data access service.
    
    Provides clean interface to:
    - Market data
    - Feature store
    - PGM predictions
    - Cached results
    """
    
    def __init__(self):
        """Initialize data service with feature store and ingestion."""
        self.feature_store = OfflineFeatureStore()
        self.data_ingestion = DataIngestion()
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        logger.info("DataService initialized")
    
    # ========================================================================
    # RAW MARKET DATA
    # ========================================================================
    
    def get_latest_stock_data(self, symbol: str, days: int = 1) -> Optional[pd.DataFrame]:
        """
        Get latest stock price data from yfinance.
        
        Args:
            symbol: Stock ticker symbol
            days: Number of days of history to fetch
            
        Returns:
            DataFrame with OHLCV data or None if not available
        """
        try:
            cache_key = f"stock_data_{symbol}_{days}"
            if self._is_cached(cache_key):
                logger.debug(f"Returning cached stock data for {symbol}")
                return self._cache[cache_key]['data']
            
            logger.info(f"Fetching latest stock data for {symbol}")
            
            # Fetch from yfinance
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Use fetch_latest for recent data
            df = self.data_ingestion.fetch_latest(
                ticker=symbol,
                lookback_days=days
            )
            
            if df is None or df.empty:
                logger.warning(f"No stock data available for {symbol}")
                return None
            
            # Cache result
            self._set_cache(cache_key, df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_multiple_stocks_data(self, symbols: List[str], days: int = 1) -> Dict[str, pd.DataFrame]:
        """
        Get latest data for multiple symbols.
        
        Args:
            symbols: List of stock ticker symbols
            days: Number of days of history
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        for symbol in symbols:
            df = self.get_latest_stock_data(symbol, days)
            if df is not None:
                results[symbol] = df
        return results
    
    # ========================================================================
    # ENGINEERED FEATURES
    # ========================================================================
    
    def get_latest_features(self, symbol: str) -> Optional[pd.Series]:
        """
        Get latest engineered features for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Series with latest features or None if not available
        """
        try:
            cache_key = f"features_{symbol}"
            if self._is_cached(cache_key):
                logger.debug(f"Returning cached features for {symbol}")
                return self._cache[cache_key]['data']
            
            logger.info(f"Fetching latest features for {symbol}")
            
            # Read from feature store
            features_df = self.feature_store.read_features(
                feature_group='market_features',
                version='v1',
                use_latest=True
            )
            
            if features_df is None or features_df.empty:
                logger.warning(f"No features found in feature store")
                return None
            
            # Filter for symbol
            if 'ticker' in features_df.columns:
                symbol_df = features_df[features_df['ticker'] == symbol]
            else:
                logger.warning(f"No 'ticker' column in features")
                return None
            
            if symbol_df.empty:
                logger.warning(f"No features found for {symbol}")
                return None
            
            # Get latest row
            if 'date' in symbol_df.columns:
                symbol_df = symbol_df.sort_values('date', ascending=False)
            
            latest = symbol_df.iloc[0]
            
            # Cache result
            self._set_cache(cache_key, latest)
            
            return latest
            
        except Exception as e:
            logger.error(f"Error fetching features for {symbol}: {e}")
            return None
    
    def get_historical_features(
        self, 
        symbol: str, 
        days: int = 30
    ) -> Optional[pd.DataFrame]:
        """
        Get historical features for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            days: Number of days of history
            
        Returns:
            DataFrame with historical features or None
        """
        try:
            logger.info(f"Fetching {days} days of features for {symbol}")
            
            # Read from feature store
            features_df = self.feature_store.read_features(
                feature_group='market_features',
                version='v1',
                use_latest=True
            )
            
            if features_df is None or features_df.empty:
                return None
            
            # Filter for symbol
            if 'ticker' in features_df.columns:
                symbol_df = features_df[features_df['ticker'] == symbol]
            else:
                return None
            
            if symbol_df.empty:
                return None
            
            # Sort by date and get last N days
            if 'date' in symbol_df.columns:
                symbol_df = symbol_df.sort_values('date', ascending=False)
                symbol_df = symbol_df.head(days)
                symbol_df = symbol_df.sort_values('date', ascending=True)
            
            return symbol_df
            
        except Exception as e:
            logger.error(f"Error fetching historical features for {symbol}: {e}")
            return None
    
    # ========================================================================
    # PGM PREDICTIONS
    # ========================================================================
    
    def get_pgm_predictions(
        self, 
        symbol: str, 
        pgm_service
    ) -> Optional[Dict[str, Any]]:
        """
        Get PGM predictions for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            pgm_service: PGM service instance
            
        Returns:
            Dictionary with probabilities and confidence or None
        """
        try:
            logger.info(f"Getting PGM predictions for {symbol}")
            
            # Get latest features
            features = self.get_latest_features(symbol)
            if features is None:
                logger.warning(f"No features available for {symbol}")
                return None
            
            # Convert Series to DataFrame (encode_features expects DataFrame)
            if isinstance(features, pd.Series):
                features = features.to_frame().T
            
            # Encode features
            encoded = pgm_service.encode_features(features)
            
            # Build evidence
            evidence = pgm_service.build_evidence(encoded)
            
            # Perform inference
            result = pgm_service.inference_engine.query(['future_return_state'], evidence)
            probabilities = result.get('future_return_state', {})
            
            if not probabilities:
                logger.warning(f"No probabilities returned for {symbol}")
                return None
            
            # Determine confidence
            max_prob = max(probabilities.values())
            confidence = pgm_service.categorize_confidence(max_prob)
            
            # Get signal
            signals = pgm_service.inference_engine.compute_signal_probabilities(evidence)
            best_signal = max(signals, key=signals.get) if signals else 'HOLD'
            
            return {
                'probabilities': probabilities,
                'confidence': confidence,
                'signal': best_signal.upper(),
                'signal_probabilities': signals
            }
            
        except Exception as e:
            logger.error(f"Error getting PGM predictions for {symbol}: {e}")
            return None
    
    def get_pgm_explanation(
        self, 
        symbol: str, 
        pgm_service
    ) -> Optional[Dict[str, Any]]:
        """
        Get PGM explanation for a symbol's prediction.
        
        Args:
            symbol: Stock ticker symbol
            pgm_service: PGM service instance
            
        Returns:
            Dictionary with explanation details or None
        """
        try:
            logger.info(f"Getting PGM explanation for {symbol}")
            
            # Get features and evidence
            features = self.get_latest_features(symbol)
            if features is None:
                return None
            
            # Convert Series to DataFrame if needed
            if isinstance(features, pd.Series):
                features = features.to_frame().T
            
            encoded = pgm_service.encode_features(features)
            evidence = pgm_service.build_evidence(encoded)
            
            # Get prediction
            result = pgm_service.inference_engine.query(['future_return_state'], evidence)
            probabilities = result.get('future_return_state', {})
            
            if not probabilities:
                return None
            
            # Generate explanation
            explanation = pgm_service.explanation_engine.explain_prediction(
                'future_return_state',
                evidence,
                probabilities
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error getting PGM explanation for {symbol}: {e}")
            return None
    
    def get_regime_probabilities(
        self, 
        symbol: str, 
        pgm_service
    ) -> Optional[Dict[str, float]]:
        """
        Get market regime probabilities for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            pgm_service: PGM service instance
            
        Returns:
            Dictionary with regime probabilities or None
        """
        try:
            logger.info(f"Getting regime probabilities for {symbol}")
            
            features = self.get_latest_features(symbol)
            if features is None:
                return None
            
            # Convert Series to DataFrame (encode_features expects DataFrame)
            if isinstance(features, pd.Series):
                features = features.to_frame().T
            
            encoded = pgm_service.encode_features(features)
            evidence = pgm_service.build_evidence(encoded)
            
            # Query regime
            result = pgm_service.inference_engine.query(['regime_state'], evidence)
            regime_probs = result.get('regime_state', {})
            
            if not regime_probs:
                return None
            
            # Ensure all regime types
            return {
                'bull': regime_probs.get('bull', 0.0),
                'bear': regime_probs.get('bear', 0.0),
                'sideways': regime_probs.get('sideways', 0.0),
                'current': max(regime_probs, key=regime_probs.get) if regime_probs else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error getting regime for {symbol}: {e}")
            return None
    
    # ========================================================================
    # PRECOMPUTED RESULTS
    # ========================================================================
    
    def get_baseline_comparison(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Load precomputed baseline comparison results.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with comparison results or None
        """
        try:
            comparison_file = Path(f'data/baseline_comparison/{symbol}_comparison.json')
            if not comparison_file.exists():
                logger.warning(f"No baseline comparison found for {symbol}")
                return None
            
            with open(comparison_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded baseline comparison for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading baseline comparison for {symbol}: {e}")
            return None
    
    def get_calibration_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Load precomputed calibration analysis results.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with calibration results or None
        """
        try:
            calibration_file = Path(f'data/calibration/{symbol}_calibration.json')
            if not calibration_file.exists():
                logger.warning(f"No calibration analysis found for {symbol}")
                return None
            
            with open(calibration_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded calibration analysis for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading calibration analysis for {symbol}: {e}")
            return None
    
    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is in cache and not expired."""
        if key not in self._cache:
            return False
        
        cached_time = self._cache[key]['timestamp']
        age = (datetime.now() - cached_time).total_seconds()
        
        return age < self._cache_ttl
    
    def _set_cache(self, key: str, data: Any):
        """Store data in cache with timestamp."""
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache = {}
        logger.info("Cache cleared")
