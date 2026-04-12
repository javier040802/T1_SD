import redis
import json
import time

r = redis.Redis(host='redis', port=6379, decode_responses=True)

def get_or_set(key, func, ttl=60):
    start = time.time()

    value = r.get(key)
    if value:
        return json.loads(value), True, time.time() - start

    result = func()
    r.setex(key, ttl, json.dumps(result))

    return result, False, time.time() - start
