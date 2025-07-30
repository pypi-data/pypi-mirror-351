"""
Real-time feature store for fraud detection.

Provides high-performance feature storage and computation using Redis
with optimized sliding windows and aggregation functions.
"""

from .base import (
    DEFAULT_FEATURE_DEFINITIONS,
    FeatureDefinition,
    FeatureRequest,
    FeatureResponse,
    FeatureStore,
    FeatureType,
    PaymentAttempt,
)
from .redis_store import RedisFeatureStore
from .sliding_window import (
    ConfigurableIPWindow,
    ConfigurableWindow,
    IPWindow,
    SlidingWindow,
    make_window,
)

__all__ = [
    # Base interfaces
    "FeatureStore",
    "FeatureDefinition",
    "FeatureRequest",
    "FeatureResponse",
    "FeatureType",
    "PaymentAttempt",
    "DEFAULT_FEATURE_DEFINITIONS",
    # Implementations
    "RedisFeatureStore",
    # Sliding windows
    "SlidingWindow",
    "ConfigurableWindow",
    "IPWindow",
    "ConfigurableIPWindow",
    "make_window",
]
