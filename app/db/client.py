# app/db/client.py
from redis import Redis
import redis.asyncio as aioredis
from .config import redis_config


# Create synchronous Redis client
sync_redis_client = Redis.from_url(
    redis_config.connection_url,
    db=redis_config.db_index,
    decode_responses=False,
)

# Create asynchronous Redis client
# This client is designed for use with async/await patterns and asyncio event loops.
async_redis_client = aioredis.from_url(
    redis_config.connection_url,
    db=redis_config.db_index,
    decode_responses=False,
)