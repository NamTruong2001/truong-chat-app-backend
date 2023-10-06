import redis
from global_variables import REDIS_PASSWORD, REDIS_PORT, REDIS_DB, REDIS_HOST

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=None, decode_responses=True)