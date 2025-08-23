from redis.asyncio import Redis
from config import settings


_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if not _redis:
        _redis = Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
    return _redis
