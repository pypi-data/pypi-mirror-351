"""
Redis sink module for efficient feature storage.
"""

from .pipeline import RedisError, RedisPipeline

__all__ = ["RedisPipeline", "RedisError"]
