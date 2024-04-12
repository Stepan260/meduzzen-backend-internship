import redis.asyncio as redis

from app.сore.config import settings


redis_connection = redis.from_url(settings.REDIS_URL, decode_responses=True)
