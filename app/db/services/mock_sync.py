# app/db/services/mock_sync.py
import time
from typing import Any
from ..config import redis_config
from ..serializers import JsonSerializer, PickleSerializer
from ..decorators import redis_cached, invalidate_redis_cache


class MockSyncService:
    """
    Mock synchronous service demonstrating Redis caching patterns.

    Simulates typical operations with varying computational cost:
    - Fast API operations (use JSON + ttl_fast)
    - Slow/expensive ML operations (use Pickle + ttl_slow)
    """

    @redis_cached(
        ttl=redis_config.ttl_slow, 
        serializer=PickleSerializer()
    )
    def run_prediction(self, model_id: str, input_data: list[float]) -> dict[str, Any]:
        """
        Simulate running ML model inference.

        Result is cached with long TTL because inference is expensive.
        Uses Pickle to support complex output structures.

        Parameters
        ----------
        model_id : str
            Identifier of the model to use.
        input_data : list[float]
            Input features for prediction.

        Returns
        -------
        dict[str, Any]
            Prediction result (e.g., probabilities, labels).
        """

        time.sleep(20)  # Simulate heavy computation
        return {
            "model_id": model_id,
            "prediction": [x * 0.5 for x in input_data],
            "confidence": 0.95
        }

    @redis_cached(
        ttl=redis_config.ttl_fast, 
        serializer=JsonSerializer()
    )
    def get_user(self, user_id: int) -> dict[str, Any]:
        """
        Simulate retrieving a user profile from a database.

        Fast operation; result is JSON-serializable and cached briefly.

        Parameters
        ----------
        user_id : int
            Unique user identifier.

        Returns
        -------
        dict[str, Any]
            User profile data.
        """

        time.sleep(5)
        return {
            "id": user_id, 
            "name": f"User_{user_id}", 
            "email": f"user{user_id}@example.com"
        }

    @invalidate_redis_cache(target_func=get_user)
    def update_user(self, user_id: int, **updates) -> dict[str, Any]:
        """
        Simulate updating a user's profile in a database.

        Invalidates the cache for `get_user(user_id)` so next read fetches fresh data.

        Parameters
        ----------
        user_id : int
            ID of the user to update.
        **updates : dict
            Fields to update (e.g., name, email).

        Returns
        -------
        dict[str, Any]
            Updated user object.
        """

        time.sleep(5)
        return {
            "id": user_id, 
            "name": f"User_{user_id}", 
            "email": f"user{user_id}@example.com"
        }