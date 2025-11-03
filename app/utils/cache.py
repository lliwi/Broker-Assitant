"""
Redis caching utilities for sub-millisecond performance.
Reduces API calls and accelerates chart loading.
"""
import json
from typing import Any, Optional
from flask import current_app
from app import redis_client


def cache_get(key: str) -> Optional[Any]:
    """
    Retrieve value from Redis cache.

    Args:
        key: Cache key

    Returns:
        Cached value or None if not found
    """
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        current_app.logger.error(f"Cache get error for key {key}: {str(e)}")
        return None


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Store value in Redis cache with optional TTL.

    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl: Time to live in seconds (uses config default if not provided)

    Returns:
        True if successful, False otherwise
    """
    try:
        if ttl is None:
            ttl = current_app.config['CACHE_TTL_SECONDS']

        serialized = json.dumps(value)
        redis_client.setex(key, ttl, serialized)
        return True
    except Exception as e:
        current_app.logger.error(f"Cache set error for key {key}: {str(e)}")
        return False


def cache_delete(key: str) -> bool:
    """
    Delete key from Redis cache.

    Args:
        key: Cache key

    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        current_app.logger.error(f"Cache delete error for key {key}: {str(e)}")
        return False


def cache_exists(key: str) -> bool:
    """
    Check if key exists in Redis cache.

    Args:
        key: Cache key

    Returns:
        True if key exists, False otherwise
    """
    try:
        return redis_client.exists(key) > 0
    except Exception as e:
        current_app.logger.error(f"Cache exists error for key {key}: {str(e)}")
        return False


def cache_get_or_set(key: str, callback, ttl: Optional[int] = None) -> Any:
    """
    Get value from cache or compute and cache it.

    Args:
        key: Cache key
        callback: Function to call if cache miss
        ttl: Time to live in seconds

    Returns:
        Cached or computed value
    """
    value = cache_get(key)
    if value is not None:
        return value

    value = callback()
    cache_set(key, value, ttl)
    return value


def get_price_cache_key(symbol: str, timeframe: str = '1d') -> str:
    """
    Generate standardized cache key for price data.

    Args:
        symbol: Asset symbol
        timeframe: Timeframe (1m, 5m, 15m, 1h, 1d, etc.)

    Returns:
        Cache key
    """
    return f"price:{symbol}:{timeframe}"


def get_analysis_cache_key(symbol: str, analysis_type: str) -> str:
    """
    Generate standardized cache key for analysis results.

    Args:
        symbol: Asset symbol
        analysis_type: Type of analysis (technical, fundamental, patterns)

    Returns:
        Cache key
    """
    return f"analysis:{analysis_type}:{symbol}"
