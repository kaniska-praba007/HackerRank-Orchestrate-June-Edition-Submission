import hashlib
import diskcache
from pathlib import Path

cache = diskcache.Cache(Path("cache"))

def get_cache_key(prefix: str, *args) -> str:
    """Generate a deterministic cache key."""
    raw = prefix + "||" + "||".join(str(a) for a in args)
    return hashlib.md5(raw.encode()).hexdigest()

def get_cached(key: str):
    return cache.get(key)

def set_cache(key: str, value):
    cache.set(key, value)