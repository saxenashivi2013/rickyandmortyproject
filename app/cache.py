import redis
from .config import REDIS_URL


redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def get_cache(key):
	return redis_client.get(key)


def set_cache(key, value, ex=300):
	return redis_client.set(key, value, ex=ex)
