from config import settings
import redis

redis_connection = redis.from_url(settings.REDIS_URL, decode_responses=True)
