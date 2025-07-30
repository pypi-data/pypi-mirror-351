"""
Edge-specific sliding window implementations for tracking relationships 
between entities in the fraud prevention system.
"""

import logging
import time
from collections import defaultdict, deque
from typing import Optional, Set

from prometheus_client import Counter, Gauge

from apps.feature_builder.sliding_window.window import ConfigurableWindow

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics
EDGE_WINDOW_SIZE = Gauge(
    "edge_window_size",
    "Current number of items in edge window",
    ["window_type", "edge_type"],
)
EDGE_WINDOW_SPAN = Gauge(
    "edge_window_span_seconds",
    "Time span of edge window in seconds",
    ["window_type", "edge_type"],
)
EDGE_WINDOW_ITEMS = Gauge(
    "edge_window_items",
    "Number of items for specific entity in edge window",
    ["window_type", "edge_type", "entity_id"],
)
EDGE_WINDOW_TRUNCATIONS = Counter(
    "edge_window_truncations_total",
    "Number of times edge window was truncated",
    ["window_type", "edge_type"],
)


class EdgeConfigurableWindow(ConfigurableWindow):
    """
    Extension of ConfigurableWindow that tracks edge type for each timestamp.
    Used for tracking merchants, devices, or other edge entities.
    """

    def __init__(
        self,
        window_size: int,
        max_size: int = 1000,
        window_type: str = "edge",
        edge_type: str = "merchant",
    ):
        """
        Initialize an edge-tracking configurable window.

        Args:
            window_size: Size of window in seconds
            max_size: Maximum number of items to track
            window_type: Type of window for metrics
            edge_type: Type of edge to track (merchant, device, etc.)
        """
        super().__init__(window_size, max_size, window_type)
        self.edge_type = edge_type
        self.edge_timestamps = defaultdict(
            set
        )  # Maps timestamps to sets of edge identifiers
        self.edge_last_seen = {}  # Maps edge identifiers to their last seen timestamp
        self.entity_edges = defaultdict(
            set
        )  # Maps entity_id to set of associated edge identifiers
        self.entity_count = defaultdict(int)  # Track counts per entity

        # Set initial metrics
        EDGE_WINDOW_SPAN.labels(
            window_type=self.window_type, edge_type=self.edge_type
        ).set(window_size)
        EDGE_WINDOW_SIZE.labels(
            window_type=self.window_type, edge_type=self.edge_type
        ).set(0)

    def add(
        self, timestamp: float, edge_id: str, entity_id: Optional[str] = None
    ) -> None:
        """
        Add a timestamp with edge identifier to the window.

        Args:
            timestamp: Unix timestamp
            edge_id: Identifier for the edge (merchant_id, device_id, etc.)
            entity_id: Optional entity ID for tracking counts
        """
        # Enforce max size limit
        if len(self.timestamps) >= self.max_size:
            oldest_ts = self.timestamps.popleft()

            # Clean up edge tracking for the removed timestamp
            if oldest_ts in self.edge_timestamps:
                edges = self.edge_timestamps[oldest_ts]

                # Update last seen tracking
                for edge in edges:
                    if self.edge_last_seen.get(edge) == oldest_ts:
                        self.edge_last_seen[edge] = None

                # Remove timestamp from edge tracking
                del self.edge_timestamps[oldest_ts]

            # Record metric
            EDGE_WINDOW_TRUNCATIONS.labels(
                window_type=self.window_type, edge_type=self.edge_type
            ).inc()

        # Add timestamp to window
        self.timestamps.append(timestamp)

        # Add edge ID to timestamp tracking
        self.edge_timestamps[timestamp].add(edge_id)

        # Update edge last seen time
        self.edge_last_seen[edge_id] = timestamp

        # Update entity count if provided
        if entity_id:
            self.entity_count[entity_id] = self.entity_count.get(entity_id, 0) + 1
            # Track which edges are associated with this entity
            self.entity_edges[entity_id].add(edge_id)

        # Update metrics
        EDGE_WINDOW_SIZE.labels(
            window_type=self.window_type, edge_type=self.edge_type
        ).set(len(self.timestamps))
        if entity_id:
            EDGE_WINDOW_ITEMS.labels(
                window_type=self.window_type,
                edge_type=self.edge_type,
                entity_id=entity_id,
            ).set(self.entity_count.get(entity_id, 0))

    def clean_expired(
        self, current_time: float, entity_id: Optional[str] = None
    ) -> int:
        """
        Remove expired timestamps from the window.

        Args:
            current_time: Current Unix timestamp
            entity_id: Optional entity ID for updating metrics

        Returns:
            Number of items removed
        """
        if not self.timestamps:
            return 0

        # Calculate window boundary
        boundary = current_time - self.window_size
        initial_size = len(self.timestamps)
        removed = 0

        # Track expired timestamps to remove
        expired_timestamps = []

        # Identify timestamps to remove
        while self.timestamps and self.timestamps[0] < boundary:
            expired_ts = self.timestamps.popleft()
            expired_timestamps.append(expired_ts)
            removed += 1

        # Clean up edge tracking for all expired timestamps
        for expired_ts in expired_timestamps:
            if expired_ts in self.edge_timestamps:
                edges = self.edge_timestamps[expired_ts]

                # Update last seen tracking
                for edge in edges:
                    if self.edge_last_seen.get(edge) == expired_ts:
                        self.edge_last_seen[edge] = None

                # Remove timestamp from edge tracking
                del self.edge_timestamps[expired_ts]

        # Reset entity counts if all timestamps are removed
        if not self.timestamps and entity_id in self.entity_count:
            self.entity_count[entity_id] = 0
        # Otherwise, update entity count (approximation)
        elif removed > 0 and entity_id in self.entity_count:
            # Set to zero if we removed everything
            if removed >= initial_size:
                self.entity_count[entity_id] = 0
            else:
                # This is a simplistic approach - in a real scenario we would need more detailed tracking
                self.entity_count[entity_id] = max(
                    0, self.entity_count.get(entity_id, 0) - removed
                )

        # Update metrics
        EDGE_WINDOW_SIZE.labels(
            window_type=self.window_type, edge_type=self.edge_type
        ).set(len(self.timestamps))
        if entity_id:
            EDGE_WINDOW_ITEMS.labels(
                window_type=self.window_type,
                edge_type=self.edge_type,
                entity_id=entity_id,
            ).set(self.entity_count.get(entity_id, 0))

        return removed

    def get_unique_edges(self, entity_id: Optional[str] = None) -> Set[str]:
        """
        Get the set of unique edge identifiers in the window.

        Args:
            entity_id: Optional entity ID to filter by

        Returns:
            Set of unique edge IDs with valid last_seen timestamps
        """
        # If we're not filtering by entity_id, return all unique edges
        if entity_id is None:
            return {edge for edge, ts in self.edge_last_seen.items() if ts is not None}

        # When filtering by entity_id, only return edges associated with this entity
        # that still have valid last_seen timestamps
        if entity_id in self.entity_edges:
            return {
                edge
                for edge in self.entity_edges[entity_id]
                if self.edge_last_seen.get(edge) is not None
            }

        return set()

    def count_unique_edges(self, entity_id: Optional[str] = None) -> int:
        """
        Count the number of unique edges in the window.

        Args:
            entity_id: Optional entity ID to filter by

        Returns:
            Number of unique edges
        """
        return len(self.get_unique_edges(entity_id=entity_id))

    def update_config(
        self,
        window_size: Optional[int] = None,
        max_size: Optional[int] = None,
        entity_id: Optional[str] = None,
    ) -> None:
        """
        Update window configuration at runtime.

        Args:
            window_size: New window size in seconds
            max_size: New maximum number of items
            entity_id: Optional entity ID for metrics
        """
        # Store old window size to check if it changed
        old_window_size = self.window_size
        old_size = len(self.timestamps)

        # Update configurations
        if window_size is not None:
            logger.info(
                f"Updating edge window size from {self.window_size}s to {window_size}s"
            )
            self.window_size = window_size
            EDGE_WINDOW_SPAN.labels(
                window_type=self.window_type, edge_type=self.edge_type
            ).set(window_size)

        if max_size is not None:
            # Log warning if new max size is extremely large
            if max_size > 1_000_000:
                logger.warning(
                    "Extremely large edge window max size configured during update",
                    extra={
                        "window_type": self.window_type,
                        "edge_type": self.edge_type,
                        "max_size": max_size,
                    },
                )
            self.max_size = max_size

        # Force cleanup if window size was reduced
        if window_size is not None and window_size < old_window_size:
            # Get current time once to ensure consistency
            current_time = int(time.time())
            # Calculate new boundary based on reduced window size
            window_boundary = current_time - window_size

            # Identify timestamps outside the new window boundary
            expired_timestamps = [ts for ts in self.timestamps if ts < window_boundary]
            logger.info(
                f"Edge Window shrunk: removing {len(expired_timestamps)} of {len(self.timestamps)} timestamps"
            )

            # Create a new deque with only the valid timestamps
            valid_timestamps = deque(
                [ts for ts in self.timestamps if ts >= window_boundary]
            )

            # Clean up edge tracking for expired timestamps
            for ts in expired_timestamps:
                if ts in self.edge_timestamps:
                    edges = self.edge_timestamps[ts]

                    # Check if edges appear in any valid timestamps
                    for edge in edges:
                        if not any(
                            edge in self.edge_timestamps.get(valid_ts, set())
                            for valid_ts in valid_timestamps
                        ):
                            # Edge doesn't appear in any valid timestamp
                            if self.edge_last_seen.get(edge) == ts:
                                self.edge_last_seen[edge] = None

                    # Remove timestamp from edge tracking
                    del self.edge_timestamps[ts]

            # Replace the timestamps deque
            self.timestamps = valid_timestamps

            # Update entity counts if needed (approximation)
            if entity_id in self.entity_count and expired_timestamps:
                self.entity_count[entity_id] = max(
                    0, self.entity_count.get(entity_id, 0) - len(expired_timestamps)
                )

            # Update metrics
            EDGE_WINDOW_SIZE.labels(
                window_type=self.window_type, edge_type=self.edge_type
            ).set(len(self.timestamps))
            if entity_id:
                edge_count = self.count_unique_edges()
                EDGE_WINDOW_ITEMS.labels(
                    window_type=self.window_type,
                    edge_type=self.edge_type,
                    entity_id=entity_id,
                ).set(edge_count)

            # Log the outcome
            new_size = len(self.timestamps)
            edge_count = self.count_unique_edges()
            logger.info(
                f"Edge Window cleanup: removed {old_size - new_size} timestamps, kept {new_size} timestamps, {edge_count} unique edges"
            )
        else:
            # Standard clean with the current configuration
            self.clean_expired(int(time.time()), entity_id=entity_id)
