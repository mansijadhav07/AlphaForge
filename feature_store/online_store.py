"""Online feature store using Redis."""

import json
import redis
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class OnlineFeatureStore:
    """Manage online feature storage using Redis."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: int = 0
    ):
        """
        Initialize online feature store.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
        """
        self.host = host or config.get('storage.redis.host', 'localhost')
        self.port = port or config.get('storage.redis.port', 6379)
        self.db = db or config.get('storage.redis.db', 0)
        self.key_prefix = config.get('storage.redis.key_prefix', 'feature_store')
        self.ttl = config.get('storage.redis.ttl', 86400)
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"OnlineFeatureStore connected to Redis at {self.host}:{self.port}")
        except redis.ConnectionError as e:
            logger.warning(f"Could not connect to Redis: {e}")
            logger.warning("Online feature store will not be available")
            self.client = None
    
    def write_features(
        self,
        ticker: str,
        features: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Write latest features for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            features: Dictionary of feature values
            timestamp: Feature timestamp
            
        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("Redis client not available")
            return False
        
        try:
            key = self._get_key(ticker)
            
            # Add metadata
            features['_ticker'] = ticker
            features['_timestamp'] = (timestamp or datetime.now()).isoformat()
            features['_write_time'] = datetime.now().isoformat()
            
            # Convert to JSON
            value = json.dumps(features, default=str)
            
            # Write to Redis with TTL
            self.client.setex(key, self.ttl, value)
            
            logger.debug(f"Features written to Redis for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing features to Redis: {e}")
            return False
    
    def write_batch(
        self,
        df: pd.DataFrame,
        timestamp_col: str = 'date'
    ) -> int:
        """
        Write features for multiple tickers in batch.
        
        Args:
            df: DataFrame with features (must have 'ticker' column)
            timestamp_col: Name of timestamp column
            
        Returns:
            Number of records written
        """
        if not self.client:
            logger.warning("Redis client not available")
            return 0
        
        if 'ticker' not in df.columns:
            logger.error("DataFrame must have 'ticker' column")
            return 0
        
        count = 0
        
        # Get latest record for each ticker
        latest_df = df.sort_values(timestamp_col).groupby('ticker').tail(1)
        
        for _, row in latest_df.iterrows():
            ticker = row['ticker']
            timestamp = row[timestamp_col] if timestamp_col in row else None
            
            # Convert row to dictionary, excluding non-serializable columns
            features = row.to_dict()
            
            # Remove metadata columns
            for col in ['_write_timestamp', '_version']:
                features.pop(col, None)
            
            if self.write_features(ticker, features, timestamp):
                count += 1
        
        logger.info(f"Wrote {count} feature records to Redis")
        return count
    
    def read_features(
        self,
        ticker: str,
        feature_names: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Read latest features for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            feature_names: Specific features to retrieve (None = all)
            
        Returns:
            Dictionary of feature values
        """
        if not self.client:
            logger.warning("Redis client not available")
            return None
        
        try:
            key = self._get_key(ticker)
            value = self.client.get(key)
            
            if not value:
                logger.debug(f"No features found for {ticker}")
                return None
            
            features = json.loads(value)
            
            # Filter specific features if requested
            if feature_names:
                features = {k: v for k, v in features.items() if k in feature_names or k.startswith('_')}
            
            return features
            
        except Exception as e:
            logger.error(f"Error reading features from Redis: {e}")
            return None
    
    def read_batch(
        self,
        tickers: List[str],
        feature_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Read features for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            feature_names: Specific features to retrieve
            
        Returns:
            DataFrame with features
        """
        if not self.client:
            logger.warning("Redis client not available")
            return pd.DataFrame()
        
        records = []
        
        for ticker in tickers:
            features = self.read_features(ticker, feature_names)
            if features:
                records.append(features)
        
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        logger.info(f"Read features for {len(df)} tickers from Redis")
        
        return df
    
    def delete_features(self, ticker: str) -> bool:
        """
        Delete features for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            key = self._get_key(ticker)
            self.client.delete(key)
            logger.info(f"Deleted features for {ticker}")
            return True
        except Exception as e:
            logger.error(f"Error deleting features: {e}")
            return False
    
    def list_tickers(self) -> List[str]:
        """
        List all tickers with features in the store.
        
        Returns:
            List of ticker symbols
        """
        if not self.client:
            return []
        
        try:
            pattern = f"{self.key_prefix}:*:latest"
            keys = self.client.keys(pattern)
            
            # Extract ticker from key
            tickers = [key.split(':')[1] for key in keys]
            return tickers
            
        except Exception as e:
            logger.error(f"Error listing tickers: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the online store.
        
        Returns:
            Dictionary with statistics
        """
        if not self.client:
            return {'status': 'disconnected'}
        
        try:
            info = self.client.info()
            tickers = self.list_tickers()
            
            stats = {
                'status': 'connected',
                'host': self.host,
                'port': self.port,
                'db': self.db,
                'num_tickers': len(tickers),
                'tickers': tickers,
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients')
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def clear_all(self) -> bool:
        """
        Clear all features from the store.
        
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            pattern = f"{self.key_prefix}:*"
            keys = self.client.keys(pattern)
            
            if keys:
                self.client.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys from Redis")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing store: {e}")
            return False
    
    def _get_key(self, ticker: str) -> str:
        """Generate Redis key for a ticker."""
        return f"{self.key_prefix}:{ticker}:latest"
    
    def is_connected(self) -> bool:
        """Check if Redis connection is active."""
        if not self.client:
            return False
        
        try:
            self.client.ping()
            return True
        except:
            return False
