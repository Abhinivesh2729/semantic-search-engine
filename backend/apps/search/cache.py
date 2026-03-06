import json
import hashlib
import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

_client = None


def _get_redis():
    global _client
    if _client is None:
        try:
            _client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _client.ping()
        except redis.ConnectionError:
            logger.warning("Redis unavailable, caching disabled")
            _client = None
    return _client


def get_cached(query, search_type):
    r = _get_redis()
    if not r:
        return None
    key = f"search:{search_type}:{hashlib.sha256(query.lower().strip().encode()).hexdigest()}"
    try:
        data = r.get(key)
        return json.loads(data) if data else None
    except (redis.ConnectionError, json.JSONDecodeError):
        return None


def set_cached(query, search_type, results, ttl=3600):
    r = _get_redis()
    if not r:
        return
    key = f"search:{search_type}:{hashlib.sha256(query.lower().strip().encode()).hexdigest()}"
    try:
        r.set(key, json.dumps(results), ex=ttl)
    except redis.ConnectionError:
        pass
