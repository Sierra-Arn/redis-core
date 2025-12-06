# app/db/decorators.py
from functools import wraps
from typing import Any, Callable
from asyncio import iscoroutinefunction
from .client import sync_redis_client, async_redis_client
from .serializers import Serializer


def drop_self(args):
    """
    Remove `self` -- the first argument -- from a tuple of positional arguments.

    Parameters
    ----------
    args : tuple
        Positional arguments passed to a method.

    Returns
    -------
    tuple
        Arguments without the first element.

    Notes
    -----
    This helper exists to avoid accidentally including the `self` object (i.e., the
    instance of a class) in cache key generation. Without dropping `self`, keys would
    contain unstable representations like:

        "<app.db.services.mock_sync.MockSyncService object at 0x7b110262fcb0>"

    Such memory addresses change every time an object is recreated (e.g., on notebook
    reload, process restart) making caching completely ineffective, even as a demonstration.

    While this project is educational and intentionally uses a simple key format
    (e.g., `f"{prefix}:{args}:{kwargs}"`) to keep Redis integration transparent and
    human-readable, **not all simplifications are equal**. It's perfectly reasonable
    to prioritize readable, unhashed keys for learning (this helps users inspect Redis
    directly and understand what's being cached). However, including volatile runtime
    details (like object memory addresses) is not a "simplification" — it's a
    fundamental flaw that breaks the very concept of caching.

    Therefore, even in a minimal demo, we exclude `self` to ensure keys remain
    semantically meaningful and stable across runs—without sacrificing clarity.

    Also, One might consider skipping positional arguments entirely and building cache keys
    from keyword arguments only (e.g., `prefix:{kwargs}`). However, this breaks
    correctness for functions that accept positional-only or mixed arguments.
    In Python, many calls pass data via positional arguments (e.g.,
    `run_prediction("model_a", [1,2,3])`), and these values have no corresponding
    keyword name—they simply occupy positions. If we drop `args`, two logically
    identical calls like `f(42)` and `f(x=42)` (if `x` were a keyword) would collide
    or, worse, `f(42)` and `f(99)` would map to the same key `{}` if no kwargs are
    provided, causing **incorrect cache hits**. Therefore, positional arguments must
    be included in the key—they carry essential, non-redundant information that
    kwargs alone cannot represent.
    """

    return args[1:] if args else args


def redis_cached(ttl: int, serializer: Serializer):
    """
    Factory for creating cache decorators for sync and async functions.

    Automatically caches function results in Redis using a key derived from
    the fully qualified function name and its arguments. Results are encoded
    and decoded using the provided serializer.

    Parameters
    ----------
    ttl : int
        Time-to-live (in seconds) for the cached entry.
    serializer : Serializer
        Serializer instance for converting results to/from bytes.
    """

    def decorator(func: Callable[..., Any]):
        # Automatically generate a stable, namespaced cache key prefix
        key_prefix = f"{func.__module__}.{func.__qualname__}"

        # Preserve original function's metadata (name, docstring, etc.) in the wrapper
        # so that introspection, debugging, and key generation (e.g., __qualname__) work correctly.
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = f"{key_prefix}:{drop_self(args)}:{kwargs}"
            raw_data = await async_redis_client.get(key)
            if raw_data is not None:
                return serializer.deserialize(raw_data)

            result = await func(*args, **kwargs)
            serialized = serializer.serialize(result)
            await async_redis_client.setex(key, ttl, serialized)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = f"{key_prefix}:{drop_self(args)}:{kwargs}"
            raw_data = sync_redis_client.get(key)
            if raw_data is not None:
                return serializer.deserialize(raw_data)

            result = func(*args, **kwargs)
            serialized = serializer.serialize(result)
            sync_redis_client.setex(key, ttl, serialized)
            return result

        return async_wrapper if iscoroutinefunction(func) else sync_wrapper
    return decorator


def invalidate_redis_cache(target_func: Callable):
    """
    Factory for creating cache invalidation decorators for sync and async functions.

    Parameters
    ----------
    target_func : Callable
        The function whose cache should be invalidated (e.g., get_user).
    """

    target_key_prefix = f"{target_func.__module__}.{target_func.__qualname__}"

    def decorator(mutating_func: Callable[..., Any]):
        #@wraps(mutating_func)
        async def async_wrapper(*args, **kwargs):
            result = await mutating_func(*args, **kwargs)
            key = f"{target_key_prefix}:{drop_self(args)}:{kwargs}"
            await async_redis_client.delete(key)
            return result

        #@wraps(mutating_func)
        def sync_wrapper(*args, **kwargs):
            result = mutating_func(*args, **kwargs)
            key = f"{target_key_prefix}:{drop_self(args)}:{kwargs}"
            sync_redis_client.delete(key)
            return result

        return async_wrapper if iscoroutinefunction(mutating_func) else sync_wrapper
    return decorator