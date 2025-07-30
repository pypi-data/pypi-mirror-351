"""
Sentr infrastructure components.

Provides common infrastructure utilities including Redis pooling,
JSON optimizations, settings management, and metrics collection.
"""

from .json_io import dumps, intern_feature_name, loads, serialize_features
from .metrics import track_feature_operation, track_request
from .redis_pool import (
    RedisDownError,
    create_redis_client,
    get_cache_client,
    get_feature_store_client,
)
from .settings import SentrSettings, get_settings

__all__ = [
    # Settings
    "get_settings",
    "SentrSettings",
    # Redis
    "create_redis_client",
    "get_feature_store_client",
    "get_cache_client",
    "RedisDownError",
    # JSON
    "dumps",
    "loads",
    "serialize_features",
    "intern_feature_name",
    # Metrics
    "track_request",
    "track_feature_operation",
]
