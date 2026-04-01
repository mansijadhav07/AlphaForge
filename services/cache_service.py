"""
Cache Service for AlphaForge.

Provides high-performance caching layer with:
- Redis primary cache (if available)
- In-memory fallback cache
- TTL management
- Cache invalidation
- Separate static/live data handling

Optimizes performance by:
- Caching full historical datasets
- Storing precomputed indicators
- Reducing yfinance API calls
- Enabling instant page loads
"""

import json
import pickle
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import Redis, fall back to in-memory if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache only")


class CacheService:
    """
    High-performance caching service with Redis and in-memory fallback.
    
    Features:
    - Automatic Redis/memory fallback
    - TTL-based expiration
    - Separate namespaces for different data types
    - JSON and pickle serialization support
    """
    
    def __init__(
        self,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        redis_db: int = 0,
        default_ttl: int = 300  # 5 minutes
    ):
        """
        Initialize cache service.
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            default_ttl: Default TTL in seconds
        """
        self.default_ttl = default_ttl
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._redis_client = None
        
        # Try to connect to Redis
        if REDIS_AVAILABLE:
            try:
                self._redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=False,  # We'll handle encoding
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self._redis_client.ping()
                logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache only.")
                self._redis_client = None
        
        logger.info("CacheService initialized")
    
    def _make_key(self, namespace: str, key: str) -> str:
        """Create namespaced cache key."""
        return f"alphaforge:{namespace}:{key}"
    
    # ========================================================================
    # CORE CACHE OPERATIONS
    # ========================================================================
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            namespace: Cache namespace (e.g., 'historical', 'live')
            key: Cache key (e.g., 'AAPL')
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._make_key(namespace, key)
        
        # Try Redis first
        if self._redis_client:
            try:
                value = self._redis_client.get(cache_key)
                if value:
                    logger.debug(f"Cache HIT (Redis): {cache_key}")
                    return pickle.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # Fall back to memory cache
        if cache_key in self._memory_cache:
            cached = self._memory_cache[cache_key]
            # Check expiration
            if datetime.now() < cached['expires_at']:
                logger.debug(f"Cache HIT (Memory): {cache_key}")
                return cached['value']
            else:
                # Expired, remove it
                del self._memory_cache[cache_key]
        
        logger.debug(f"Cache MISS: {cache_key}")
        return None
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
            
        Returns:
            True if successful
        """
        cache_key = self._make_key(namespace, key)
        ttl = ttl or self.default_ttl
        
        # Try Redis first
        if self._redis_client:
            try:
                serialized = pickle.dumps(value)
                self._redis_client.setex(cache_key, ttl, serialized)
                logger.debug(f"Cache SET (Redis): {cache_key}, TTL={ttl}s")
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Fall back to memory cache
        self._memory_cache[cache_key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }
        logger.debug(f"Cache SET (Memory): {cache_key}, TTL={ttl}s")
        return True
    
    def delete(self, namespace: str, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            
        Returns:
            True if deleted
        """
        cache_key = self._make_key(namespace, key)
        
        # Delete from Redis
        if self._redis_client:
            try:
                self._redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        # Delete from memory
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
        
        logger.debug(f"Cache DELETE: {cache_key}")
        return True
    
    def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace.
        
        Args:
            namespace: Cache namespace to clear
            
        Returns:
            Number of keys deleted
        """
        pattern = self._make_key(namespace, '*')
        count = 0
        
        # Clear from Redis
        if self._redis_client:
            try:
                keys = self._redis_client.keys(pattern)
                if keys:
                    count += self._redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
        
        # Clear from memory
        keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(f"alphaforge:{namespace}:")]
        for key in keys_to_delete:
            del self._memory_cache[key]
            count += 1
        
        logger.info(f"Cleared {count} keys from namespace '{namespace}'")
        return count
    
    def clear_all(self) -> bool:
        """Clear all cache data."""
        # Clear Redis
        if self._redis_client:
            try:
                keys = self._redis_client.keys("alphaforge:*")
                if keys:
                    self._redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear all error: {e}")
        
        # Clear memory
        self._memory_cache.clear()
        
        logger.info("Cleared all cache data")
        return True
    
    # ========================================================================
    # SPECIALIZED CACHE METHODS
    # ========================================================================
    
    def get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Get cached historical data for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            DataFrame with historical data or None
        """
        return self.get('historical', symbol)
    
    def set_historical_data(
        self,
        symbol: str,
        data: pd.DataFrame,
        ttl: int = 3600  # 1 hour
    ) -> bool:
        """
        Cache historical data for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            data: Historical data DataFrame
            ttl: Cache TTL in seconds (default: 1 hour)
            
        Returns:
            True if successful
        """
        return self.set('historical', symbol, data, ttl)
    
    def get_live_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cached live price for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with price and timestamp or None
        """
        return self.get('live', symbol)
    
    def set_live_price(
        self,
        symbol: str,
        price: float,
        timestamp: datetime,
        ttl: int = 30  # 30 seconds
    ) -> bool:
        """
        Cache live price for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            price: Current price
            timestamp: Price timestamp
            ttl: Cache TTL in seconds (default: 30 seconds)
            
        Returns:
            True if successful
        """
        data = {
            'price': price,
            'timestamp': timestamp.isoformat(),
            'cached_at': datetime.now().isoformat()
        }
        return self.set('live', symbol, data, ttl)
    
    def get_features(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get cached features for a symbol."""
        return self.get('features', symbol)
    
    def set_features(
        self,
        symbol: str,
        features: pd.DataFrame,
        ttl: int = 600  # 10 minutes
    ) -> bool:
        """Cache features for a symbol."""
        return self.set('features', symbol, features, ttl)
    
    # ========================================================================
    # CACHE STATISTICS
    # ========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        stats = {
            'redis_available': self._redis_client is not None,
            'memory_cache_size': len(self._memory_cache),
            'redis_keys': 0
        }
        
        if self._redis_client:
            try:
                stats['redis_keys'] = len(self._redis_client.keys("alphaforge:*"))
                stats['redis_info'] = self._redis_client.info('memory')
            except Exception as e:
                logger.warning(f"Error getting Redis stats: {e}")
        
        return stats


# Global cache instance
_cache_service = None


def get_cache_service() -> CacheService:
    """Get or create global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
