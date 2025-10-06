import redis.asyncio as redis
from app.core.config import settings

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client
