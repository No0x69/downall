import time
from collections import defaultdict

# Simple in-memory TTL cache
_cache: dict[str, tuple[float, any]] = {}
_TTL = 300  # 5 minutes

def cache_get(key: str):
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < _TTL:
            return val
        del _cache[key]
    return None

def cache_set(key: str, value):
    _cache[key] = (time.time(), value)

# Simple rate limiter — max 15 requests per IP per minute
_rate: dict[str, list[float]] = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    calls = [t for t in _rate[ip] if now - t < 60]
    _rate[ip] = calls
    if len(calls) >= 15:
        return True
    _rate[ip].append(now)
    return False
