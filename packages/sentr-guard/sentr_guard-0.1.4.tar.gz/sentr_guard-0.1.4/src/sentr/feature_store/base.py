"""
Base feature store interfaces and abstract classes.

Defines the common interface for feature storage and retrieval systems
used throughout the Sentr fraud detection pipeline.
"""

import abc
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class FeatureType(Enum):
    """Supported feature types."""

    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"
    LIST = "list"
    DICT = "dict"


@dataclass
class PaymentAttempt:
    """Payment attempt data for fraud detection."""

    ts: float
    merchant_id: str
    ip: str
    bin: Optional[str]
    amount: float


@dataclass
class FeatureDefinition:
    """Feature metadata and definition."""

    name: str
    feature_type: FeatureType
    description: str
    default_value: Any = None
    ttl_seconds: Optional[int] = None
    is_real_time: bool = True
    window_size: Optional[str] = None  # e.g., "60s", "5m", "1h"
    aggregation_method: Optional[str] = None  # e.g., "sum", "count", "avg", "max"


@dataclass
class FeatureValue:
    """Feature value with metadata."""

    name: str
    value: Any
    timestamp: datetime
    entity_id: str
    confidence: float = 1.0
    source: Optional[str] = None


@dataclass
class FeatureRequest:
    """Feature retrieval request."""

    entity_id: str
    feature_names: List[str]
    timestamp: Optional[datetime] = None
    window_size: Optional[str] = None


@dataclass
class FeatureResponse:
    """Feature retrieval response."""

    entity_id: str
    features: Dict[str, Any]
    timestamp: datetime
    missing_features: List[str]
    computed_features: List[str]
    cache_hit_ratio: float = 0.0


class FeatureStore(abc.ABC):
    """Abstract base class for feature stores."""

    @abc.abstractmethod
    async def get_features(
        self,
        entity_id: str,
        feature_names: List[str],
        timestamp: Optional[datetime] = None,
    ) -> FeatureResponse:
        """
        Retrieve features for an entity.

        Args:
            entity_id: Unique identifier for the entity
            feature_names: List of feature names to retrieve
            timestamp: Point-in-time for feature values (defaults to now)

        Returns:
            FeatureResponse with requested features
        """
        pass

    @abc.abstractmethod
    async def store_features(
        self,
        entity_id: str,
        features: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Store features for an entity.

        Args:
            entity_id: Unique identifier for the entity
            features: Dictionary of feature name -> value pairs
            timestamp: Timestamp for the features (defaults to now)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    async def update_feature(
        self,
        entity_id: str,
        feature_name: str,
        value: Any,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Update a single feature for an entity.

        Args:
            entity_id: Unique identifier for the entity
            feature_name: Name of the feature to update
            value: New value for the feature
            timestamp: Timestamp for the update (defaults to now)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    async def delete_features(
        self, entity_id: str, feature_names: Optional[List[str]] = None
    ) -> bool:
        """
        Delete features for an entity.

        Args:
            entity_id: Unique identifier for the entity
            feature_names: List of feature names to delete (None = delete all)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    async def compute_windowed_features(
        self,
        entity_id: str,
        events: List[Dict[str, Any]],
        window_definitions: List[FeatureDefinition],
    ) -> Dict[str, Any]:
        """
        Compute windowed aggregation features from events.

        Args:
            entity_id: Unique identifier for the entity
            events: List of event dictionaries
            window_definitions: Feature definitions for windowed aggregations

        Returns:
            Dictionary of computed feature values
        """
        pass

    @abc.abstractmethod
    async def get_feature_statistics(
        self, feature_names: List[str], start_time: datetime, end_time: datetime
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for features over a time range.

        Args:
            feature_names: List of feature names
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Dictionary of feature name -> statistics
        """
        pass


class WindowedFeatureCalculator(abc.ABC):
    """Abstract base class for windowed feature calculations."""

    @abc.abstractmethod
    def calculate_count(self, events: List[Dict[str, Any]], window_size: str) -> int:
        """Calculate count of events in window."""
        pass

    @abc.abstractmethod
    def calculate_sum(
        self, events: List[Dict[str, Any]], field: str, window_size: str
    ) -> float:
        """Calculate sum of field values in window."""
        pass

    @abc.abstractmethod
    def calculate_avg(
        self, events: List[Dict[str, Any]], field: str, window_size: str
    ) -> float:
        """Calculate average of field values in window."""
        pass

    @abc.abstractmethod
    def calculate_max(
        self, events: List[Dict[str, Any]], field: str, window_size: str
    ) -> Any:
        """Calculate maximum field value in window."""
        pass

    @abc.abstractmethod
    def calculate_min(
        self, events: List[Dict[str, Any]], field: str, window_size: str
    ) -> Any:
        """Calculate minimum field value in window."""
        pass

    @abc.abstractmethod
    def calculate_unique_count(
        self, events: List[Dict[str, Any]], field: str, window_size: str
    ) -> int:
        """Calculate unique count of field values in window."""
        pass


# Common feature computation utilities
def parse_window_size(window_size: str) -> timedelta:
    """
    Parse window size string to timedelta.

    Args:
        window_size: Window size string (e.g., "60s", "5m", "1h", "1d")

    Returns:
        timedelta object

    Raises:
        ValueError: If window size format is invalid
    """
    if not window_size:
        raise ValueError("Window size cannot be empty")

    # Extract number and unit
    import re

    match = re.match(r"^(\d+)([smhd])$", window_size.lower())
    if not match:
        raise ValueError(f"Invalid window size format: {window_size}")

    value, unit = match.groups()
    value = int(value)

    if unit == "s":
        return timedelta(seconds=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")


def is_event_in_window(
    event_timestamp: datetime, current_time: datetime, window_size: str
) -> bool:
    """
    Check if an event falls within a time window.

    Args:
        event_timestamp: Timestamp of the event
        current_time: Current reference time
        window_size: Window size string

    Returns:
        True if event is within window, False otherwise
    """
    window_delta = parse_window_size(window_size)
    window_start = current_time - window_delta
    return window_start <= event_timestamp <= current_time


def create_feature_key(entity_id: str, feature_name: str) -> str:
    """
    Create a standardized feature storage key.

    Args:
        entity_id: Entity identifier
        feature_name: Feature name

    Returns:
        Standardized key string
    """
    return f"feature:{entity_id}:{feature_name}"


def create_window_key(entity_id: str, feature_name: str, window_size: str) -> str:
    """
    Create a standardized windowed feature storage key.

    Args:
        entity_id: Entity identifier
        feature_name: Feature name
        window_size: Window size string

    Returns:
        Standardized windowed key string
    """
    return f"window:{entity_id}:{feature_name}:{window_size}"


# Default feature definitions for fraud detection
DEFAULT_FEATURE_DEFINITIONS = [
    FeatureDefinition(
        name="fail_60s",
        feature_type=FeatureType.NUMERICAL,
        description="Number of failed transactions in last 60 seconds",
        default_value=0,
        ttl_seconds=3600,
        window_size="60s",
        aggregation_method="count",
    ),
    FeatureDefinition(
        name="success_60s",
        feature_type=FeatureType.NUMERICAL,
        description="Number of successful transactions in last 60 seconds",
        default_value=0,
        ttl_seconds=3600,
        window_size="60s",
        aggregation_method="count",
    ),
    FeatureDefinition(
        name="amount_60s",
        feature_type=FeatureType.NUMERICAL,
        description="Total transaction amount in last 60 seconds",
        default_value=0.0,
        ttl_seconds=3600,
        window_size="60s",
        aggregation_method="sum",
    ),
    FeatureDefinition(
        name="uniq_ip_60s",
        feature_type=FeatureType.NUMERICAL,
        description="Number of unique IP addresses in last 60 seconds",
        default_value=0,
        ttl_seconds=3600,
        window_size="60s",
        aggregation_method="unique_count",
    ),
    FeatureDefinition(
        name="velocity_60s",
        feature_type=FeatureType.NUMERICAL,
        description="Transaction velocity (count per minute) in last 60 seconds",
        default_value=0.0,
        ttl_seconds=3600,
        window_size="60s",
        aggregation_method="count",
    ),
    FeatureDefinition(
        name="uniq_merchant_60s",
        feature_type=FeatureType.NUMERICAL,
        description="Number of unique merchants in last 60 seconds",
        default_value=0,
        ttl_seconds=3600,
        window_size="60s",
        aggregation_method="unique_count",
    ),
    FeatureDefinition(
        name="uniq_device_60s",
        feature_type=FeatureType.NUMERICAL,
        description="Number of unique devices in last 60 seconds",
        default_value=0,
        ttl_seconds=3600,
        window_size="60s",
        aggregation_method="unique_count",
    ),
]
