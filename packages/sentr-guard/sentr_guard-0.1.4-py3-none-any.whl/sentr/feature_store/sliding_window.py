"""
Optimized sliding window implementations for real-time feature calculation.

Moved from apps/feature_builder/sliding_window/window.py for the new feature store architecture.
"""

import logging
import os
import time
from collections import deque
from typing import Set

import prometheus_client as prom

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics for window monitoring
try:
    WINDOW_TRUNCATIONS = prom.Counter(
        "window_truncations_total",
        "Number of times a window was truncated due to max size",
        ["window_type"],
    )
except ValueError:
    from prometheus_client import REGISTRY

    WINDOW_TRUNCATIONS = REGISTRY.get_sample_value("window_truncations_total")

try:
    WINDOW_SIZE = prom.Gauge(
        "window_size", "Number of items in window", ["window_type"]
    )
except ValueError:
    from prometheus_client import REGISTRY

    WINDOW_SIZE = REGISTRY.get_sample_value("window_size")

try:
    WINDOW_SPAN = prom.Gauge(
        "window_span_seconds", "Time span of sliding window in seconds", ["window_type"]
    )
except ValueError:
    from prometheus_client import REGISTRY

    WINDOW_SPAN = REGISTRY.get_sample_value("window_span_seconds")


# Dummy no-op implementation to avoid code changes elsewhere
class NoOpGauge:
    def labels(self, **kwargs):
        return self

    def set(self, value):
        pass


WINDOW_ITEMS = NoOpGauge()

# Default configuration
DEFAULT_WINDOW_MAX_SIZE = int(os.environ.get("WINDOW_MAX_SIZE", "10000"))
DEFAULT_LONG_WINDOW_MAX_SIZE = int(os.environ.get("LONG_WINDOW_MAX_SIZE", "100000"))
DEFAULT_WINDOW_SIZE = int(os.environ.get("WINDOW_SIZE", "60"))  # 60 seconds
DEFAULT_LONG_WINDOW_SIZE = int(
    os.environ.get("LONG_WINDOW_SIZE", "604800")
)  # 7 days in seconds
DEFAULT_PIPELINE_SIZE = int(os.environ.get("REDIS_PIPELINE_SIZE", "500"))
DEFAULT_PIPELINE_FLUSH_MS = int(os.environ.get("REDIS_PIPELINE_FLUSH_MS", "10"))


class SlidingWindow:
    """
    Memory-efficient sliding window implementation with size limits.

    Uses a deque for O(1) append and popleft operations, with optimized
    cleaning strategies for expired timestamps.
    """

    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        max_size: int = DEFAULT_WINDOW_MAX_SIZE,
    ):
        """
        Initialize a sliding window.

        Args:
            window_size: Time window size in seconds
            max_size: Maximum number of elements to store (prevents memory explosion)
        """
        self.window_size = window_size
        self.max_size = max_size
        self.timestamps = deque()

    def add(self, timestamp: float) -> None:
        """
        Add a timestamp to the window, enforcing max_size limit.

        If the window is at max capacity, the oldest element will be removed
        before adding the new one.

        Args:
            timestamp: Unix timestamp to add to the window
        """
        if len(self.timestamps) >= self.max_size:
            self.timestamps.popleft()
            WINDOW_TRUNCATIONS.labels(window_type="sliding").inc()

        self.timestamps.append(timestamp)
        WINDOW_SIZE.labels(window_type="sliding").set(len(self.timestamps))

    def clean_expired(self, current_time: float) -> None:
        """
        Remove expired timestamps more efficiently.

        Uses optimized strategies for different scenarios:
        1. Empty window or fully expired window: Clear all
        2. No expired items: Do nothing
        3. Some expired items: Remove only what's needed

        Args:
            current_time: Current time to use for expiration calculation
        """
        cutoff = current_time - self.window_size

        # Optimization: if window empty or newest timestamp is expired, clear all
        if not self.timestamps or self.timestamps[-1] < cutoff:
            self.timestamps.clear()
            WINDOW_SIZE.labels(window_type="sliding").set(0)
            return

        # Optimization: if oldest timestamp is not expired, do nothing
        if self.timestamps[0] >= cutoff:
            return

        # Remove expired timestamps from the front of the deque
        initial_size = len(self.timestamps)
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()

        # Update metrics if we removed items
        if initial_size != len(self.timestamps):
            WINDOW_SIZE.labels(window_type="sliding").set(len(self.timestamps))

    def count(self) -> int:
        """
        Get current count of items in the window.

        Returns:
            Number of timestamps in the window
        """
        return len(self.timestamps)


class ConfigurableWindow(SlidingWindow):
    """
    Enhanced sliding window with configurable parameters and memory management.

    Provides better memory management and configuration options for different
    use cases while preventing memory leaks through proper cleanup.
    """

    def __init__(
        self, window_size=60, max_size=DEFAULT_WINDOW_MAX_SIZE, window_type="default"
    ):
        """
        Initialize a configurable sliding window.

        Args:
            window_size: Time window size in seconds
            max_size: Maximum number of elements to store
            window_type: Type identifier for metrics
        """
        super().__init__(window_size, max_size)
        self.window_type = window_type
        self._last_cleanup = time.time()
        self._cleanup_interval = 30  # Cleanup every 30 seconds

        # Initialize metrics
        WINDOW_SIZE.labels(window_type=window_type).set(0)
        WINDOW_SPAN.labels(window_type=window_type).set(0)

    def add(self, timestamp, entity_id=None):
        """
        Add an item to the window with automatic cleanup.

        Args:
            timestamp: Unix timestamp
            entity_id: Optional entity identifier (for tracking purposes)
        """
        current_time = time.time()

        # Use provided timestamp or current time
        if timestamp is None:
            timestamp = current_time

        # Add to the window
        super().add(timestamp)

        # Periodic cleanup to prevent memory leaks
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.clean_expired(current_time)
            self._last_cleanup = current_time

        # Update metrics
        self._update_metrics()

    def clean_expired(self, current_time, entity_id=None):
        """
        Clean expired items with enhanced memory management.

        Args:
            current_time: Current timestamp for expiration calculation
            entity_id: Optional entity identifier (unused in base implementation)
        """
        initial_size = len(self.timestamps)

        # Call parent cleanup
        super().clean_expired(current_time)

        # Update metrics if items were removed
        if len(self.timestamps) != initial_size:
            self._update_metrics()

        # Log significant cleanup events
        removed_count = initial_size - len(self.timestamps)
        if removed_count > 100:  # Log if we removed many items
            logger.debug(
                f"Cleaned {removed_count} expired items from {self.window_type} window"
            )

    def _update_metrics(self):
        """Update Prometheus metrics for this window"""
        current_size = len(self.timestamps)
        WINDOW_SIZE.labels(window_type=self.window_type).set(current_size)

        # Calculate time span if we have data
        if current_size > 1:
            span = self.timestamps[-1] - self.timestamps[0]
            WINDOW_SPAN.labels(window_type=self.window_type).set(span)
        else:
            WINDOW_SPAN.labels(window_type=self.window_type).set(0)

    @property
    def size(self):
        """Return the current number of elements in the window"""
        # Clean expired items before returning size
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.clean_expired(current_time)
            self._last_cleanup = current_time
        return len(self.timestamps)

    def update_config(self, window_size=None, max_size=None, entity_id=None):
        """
        Update window configuration with proper cleanup.

        Args:
            window_size: New window size in seconds
            max_size: New maximum size
            entity_id: Optional entity identifier (unused in base implementation)
        """
        config_changed = False

        if window_size is not None and window_size != self.window_size:
            self.window_size = window_size
            config_changed = True

        if max_size is not None and max_size != self.max_size:
            self.max_size = max_size
            config_changed = True

        # If configuration changed, clean up immediately
        if config_changed:
            current_time = time.time()
            self.clean_expired(current_time)

            # Enforce new max size
            if len(self.timestamps) > self.max_size:
                # Remove oldest items to fit new max size
                excess = len(self.timestamps) - self.max_size
                for _ in range(excess):
                    self.timestamps.popleft()
                WINDOW_TRUNCATIONS.labels(window_type=self.window_type).inc(excess)

            self._update_metrics()
            logger.debug(
                f"Updated {self.window_type} window config: size={self.window_size}s, max={self.max_size}"
            )

    def count(self, entity_id=None):
        """
        Count items in the window with automatic cleanup.

        Args:
            entity_id: Optional entity identifier (unused in base implementation)

        Returns:
            Number of items in the window
        """
        current_time = time.time()
        self.clean_expired(current_time)
        return len(self.timestamps)


class IPWindow:
    """
    Window for tracking unique IP addresses over a time period.
    Used for features like 'number of unique IPs per card in last 60s'.
    """

    def __init__(
        self, window_size=DEFAULT_WINDOW_SIZE, max_size=DEFAULT_WINDOW_MAX_SIZE
    ):
        """
        Initialize a window for tracking unique IPs.

        Args:
            window_size: Time window size in seconds
            max_size: Maximum number of elements to store
        """
        self.window_size = window_size
        self.max_size = max_size

        # Map of timestamp -> set of IPs seen at that time
        self.ip_timestamps = {}

        # Map of IP -> timestamp last seen (for faster lookups)
        self.ip_last_seen = {}

    def add(self, timestamp: float, ip: str) -> None:
        """
        Add an IP address seen at the given timestamp.

        Args:
            timestamp: Unix timestamp when IP was seen
            ip: IP address as string
        """
        # Enforce max size limit - remove oldest if full
        if (
            len(self.ip_timestamps) >= self.max_size
            and timestamp not in self.ip_timestamps
        ):
            if self.ip_timestamps:
                # Find oldest timestamp
                oldest = min(self.ip_timestamps.keys())
                # Get IPs from oldest timestamp
                ips_to_remove = self.ip_timestamps[oldest]
                # Update IP tracking
                for old_ip in ips_to_remove:
                    # Only remove tracking if this was the last time seen
                    if self.ip_last_seen.get(old_ip) == oldest:
                        self.ip_last_seen[old_ip] = None
                # Remove oldest timestamp
                del self.ip_timestamps[oldest]

        # Add IP to this timestamp
        if timestamp not in self.ip_timestamps:
            self.ip_timestamps[timestamp] = set()
        self.ip_timestamps[timestamp].add(ip)

        # Update last seen time for this IP
        self.ip_last_seen[ip] = timestamp

    def clean_expired(self, current_time: float) -> None:
        """
        Remove expired IP timestamps.

        Args:
            current_time: Current time for expiration calculation
        """
        cutoff = current_time - self.window_size

        # Find expired timestamps
        expired = [ts for ts in self.ip_timestamps if ts < cutoff]

        # Remove expired timestamps and update IP tracking
        for ts in expired:
            # Get IPs at this timestamp
            ips = self.ip_timestamps[ts]

            # Update IP tracking
            for ip in ips:
                if self.ip_last_seen.get(ip) == ts:
                    self.ip_last_seen[ip] = None

            # Remove timestamp
            del self.ip_timestamps[ts]

    def get_unique_ips(self) -> Set[str]:
        """
        Get set of unique IPs in the window.

        Returns:
            Set of unique IP addresses in current window
        """
        result = set()
        # Only include IPs that have been seen (not None in last_seen)
        for ip, last_seen in self.ip_last_seen.items():
            if last_seen is not None:
                result.add(ip)
        return result

    def count_unique(self) -> int:
        """
        Get the count of unique IP addresses in the window.

        Returns:
            Number of unique IP addresses
        """
        return len(self.get_unique_ips())


class ConfigurableIPWindow(IPWindow):
    """
    Enhanced IP window with configurable parameters and memory management.

    Provides better memory management and configuration options for IP tracking
    while preventing memory leaks through proper cleanup.
    """

    def __init__(
        self, window_size=60, max_size=DEFAULT_WINDOW_MAX_SIZE, window_type="ip"
    ):
        """
        Initialize a configurable IP window.

        Args:
            window_size: Time window size in seconds
            max_size: Maximum number of timestamps to store
            window_type: Type identifier for metrics
        """
        super().__init__(window_size, max_size)
        self.window_type = window_type
        self._last_cleanup = time.time()
        self._cleanup_interval = 30  # Cleanup every 30 seconds

        # Initialize metrics
        WINDOW_SIZE.labels(window_type=window_type).set(0)
        WINDOW_SPAN.labels(window_type=window_type).set(0)

    def add(self, timestamp: float, ip: str, entity_id: str = None) -> None:
        """
        Add an IP address with automatic cleanup.

        Args:
            timestamp: Unix timestamp when IP was seen
            ip: IP address as string
            entity_id: Optional entity identifier (for tracking purposes)
        """
        current_time = time.time()

        # Use provided timestamp or current time
        if timestamp is None:
            timestamp = current_time

        # Add to the window
        super().add(timestamp, ip)

        # Periodic cleanup to prevent memory leaks
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.clean_expired(current_time)
            self._last_cleanup = current_time

        # Update metrics
        self._update_metrics()

    @property
    def size(self):
        """Return the current number of timestamps in the window"""
        # Clean expired items before returning size
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.clean_expired(current_time)
            self._last_cleanup = current_time
        return len(self.ip_timestamps)

    def clean_expired(self, current_time: float, entity_id: str = None) -> int:
        """
        Clean expired IP data with enhanced memory management.

        Args:
            current_time: Current timestamp for expiration calculation
            entity_id: Optional entity identifier (unused in base implementation)

        Returns:
            Number of timestamps removed
        """
        initial_size = len(self.ip_timestamps)

        # Call parent cleanup
        super().clean_expired(current_time)

        # Update metrics if items were removed
        removed_count = initial_size - len(self.ip_timestamps)
        if removed_count > 0:
            self._update_metrics()

            # Log significant cleanup events
            if removed_count > 10:
                logger.debug(
                    f"Cleaned {removed_count} expired IP timestamps from {self.window_type} window"
                )

        return removed_count

    def _update_metrics(self):
        """Update Prometheus metrics for this IP window"""
        current_size = len(self.ip_timestamps)
        WINDOW_SIZE.labels(window_type=self.window_type).set(current_size)

        # Calculate time span if we have data
        if current_size > 1:
            timestamps = list(self.ip_timestamps.keys())
            span = max(timestamps) - min(timestamps)
            WINDOW_SPAN.labels(window_type=self.window_type).set(span)
        else:
            WINDOW_SPAN.labels(window_type=self.window_type).set(0)

    def update_config(self, window_size=None, max_size=None, entity_id=None):
        """
        Update window configuration with proper cleanup.

        Args:
            window_size: New window size in seconds
            max_size: New maximum size
            entity_id: Optional entity identifier (unused in base implementation)
        """
        config_changed = False
        old_window_size = self.window_size

        if window_size is not None and window_size != self.window_size:
            self.window_size = window_size
            config_changed = True

        if max_size is not None and max_size != self.max_size:
            self.max_size = max_size
            config_changed = True

        # If configuration changed, clean up immediately
        if config_changed:
            current_time = time.time()
            self.clean_expired(current_time)
            self._update_metrics()
            logger.debug(
                f"Updated {self.window_type} IP window config: size={self.window_size}s, max={self.max_size}"
            )

    def count_unique(self):
        """
        Get the count of unique IP addresses in the window.

        Returns:
            Number of unique IP addresses
        """
        return len(self.get_unique_ips())


def make_window(kind="default", long=False, merchant_id=None, edge_type=None):
    """
    Factory function to create appropriate window type with proper configuration.

    Args:
        kind: The kind of window to create ("default", "ip", "merchant", "device")
        long: Whether to create a long-term window
        merchant_id: Optional merchant ID for merchant-specific configuration
        edge_type: Optional edge type for edge-based windows

    Returns:
        Appropriate window instance with correct configuration
    """
    # Use environment variables for configuration
    default_window_size = 60  # Default short window (60s)
    default_long_window_size = 7 * 24 * 3600  # Default long window (7 days)

    # Default max sizes - more reasonable calculation based on update frequency
    default_window_max_size = 1_000  # Short window typically needs fewer entries
    default_long_window_max_size = 604_800  # 1 transaction per second for 7 days

    window_size = int(
        os.environ.get(
            "LONG_WINDOW_SIZE" if long else "WINDOW_SIZE",
            default_long_window_size if long else default_window_size,
        )
    )

    max_size = int(
        os.environ.get(
            "LONG_WINDOW_MAX_SIZE" if long else "WINDOW_MAX_SIZE",
            default_long_window_max_size if long else default_window_max_size,
        )
    )

    # Generate a window type string for metrics
    window_type = f"{kind}{'_long' if long else ''}"

    # Create the appropriate window type
    if kind == "ip":
        return ConfigurableIPWindow(
            window_size=window_size, max_size=max_size, window_type=window_type
        )
    else:
        return ConfigurableWindow(
            window_size=window_size, max_size=max_size, window_type=window_type
        )
