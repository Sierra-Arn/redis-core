# app/db/client.py
from redis import Redis
import redis.asyncio as aioredis
from .config import redis_config


sync_redis_client = Redis.from_url(
    redis_config.connection_url,
    db=redis_config.db_index,
    decode_responses=redis_config.decode_responses,
)
"""
Synchronous Redis client configured via application settings.

This client provides the foundational connection interface for all synchronous
cache operations against the Redis instance.
"""

async_redis_client = aioredis.from_url(
    redis_config.connection_url,
    db=redis_config.db_index,
    decode_responses=redis_config.decode_responses,
)
"""
Asynchronous Redis client configured via application settings.

This client provides the foundational connection interface for all asynchronous
cache operations against the Redis instance.
"""