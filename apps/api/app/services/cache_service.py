import json
from typing import Optional

from app.core.redis import redis_client


def set_cache(key: str, value: dict, expire: int = 3600) -> bool:
    """Set a value in Redis cache.

    Args:
        key: Cache key
        value: Dictionary value to cache
        expire: Expiration time in seconds (default 3600)

    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client.set(key, json.dumps(value), ex=expire)
        return True
    except Exception as e:
        print(f"Error setting cache for key {key}: {e}")
        return False


def get_cache(key: str) -> Optional[dict]:
    """Get a value from Redis cache.

    Args:
        key: Cache key

    Returns:
        Dictionary value if found, None otherwise
    """
    try:
        data = redis_client.get(key)

        if data:
            return json.loads(data)

        return None
    except Exception as e:
        print(f"Error getting cache for key {key}: {e}")
        return None
