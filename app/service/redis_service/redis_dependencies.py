import redis

from config import get_settings

settings = get_settings()
redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=None, decode_responses=True)