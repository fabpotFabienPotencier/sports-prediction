from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from typing import Any, Callable
from functools import wraps
from app.config import get_settings

settings = get_settings()

async def init_cache():
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="sports-prediction-")

def custom_cache(
    expire: int = 60,
    key_builder: Callable = None
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache_key = key_builder(*args, **kwargs) if key_builder else f"{func.__name__}:{args}:{kwargs}"
            
            # Try to get from cache
            cached_result = await FastAPICache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # If not in cache, execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await FastAPICache.set(cache_key, result, expire=expire)
            
            return result
        return wrapper
    return decorator 