import redis.asyncio as redis

from app.сore.config import settings


async def check_redis_connection():
    try:
        connection = await redis.from_url(settings.REDIS_URL)
        await connection.set("test_key", "test_value")
        value = await connection.get("test_key")
        await connection.close()
        if value == b"test_value":
            return True
        else:
            return False
    except Exception:
        return False
