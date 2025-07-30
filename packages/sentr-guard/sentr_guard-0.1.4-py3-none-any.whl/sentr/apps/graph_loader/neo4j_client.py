"""
Neo4j database client for the Graph Loader service.
Handles connections, queries, and metrics for Neo4j operations.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase
from prometheus_client import Counter, Gauge, Histogram

from apps.graph_loader.config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics
NEO4J_QUERY_DURATION = Histogram(
    "neo4j_query_duration_seconds", "Time spent executing Neo4j queries", ["query_type"]
)
NEO4J_QUERIES_TOTAL = Counter(
    "neo4j_queries_total",
    "Total number of Neo4j queries executed",
    ["query_type", "status"],
)
LOADED_EDGES_TOTAL = Counter(
    "loaded_edges_total",
    "Total number of edges loaded into Neo4j by type",
    ["edge_type"],
)
NEO4J_CONNECTION_STATUS = Gauge(
    "neo4j_connection_status", "Neo4j connection status (1=connected, 0=disconnected)"
)


class Neo4jClient:
    """Client for interacting with Neo4j graph database."""

    def __init__(
        self,
        uri: str = NEO4J_URI,
        user: str = NEO4J_USER,
        password: str = NEO4J_PASSWORD,
    ):
        """Initialize Neo4j client."""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.connect()

    def connect(self) -> bool:
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            # Verify connection is working
            with self.driver.session() as session:
                session.run("RETURN 1").single()
            logger.info(f"Connected to Neo4j at {self.uri}")
            NEO4J_CONNECTION_STATUS.set(1)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            NEO4J_CONNECTION_STATUS.set(0)
            return False

    def close(self) -> None:
        """Close connection to Neo4j."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
            NEO4J_CONNECTION_STATUS.set(0)

    def run(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        query_type: str = "unknown",
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query with parameters and return results.

        Args:
            query: Cypher query string
            params: Query parameters
            query_type: Type of query for metrics (e.g., "create_card_ip", "create_card_merchant")

        Returns:
            List of result records as dictionaries
        """
        start_time = time.time()
        params = params or {}

        try:
            if not self.driver or not self._is_connected():
                logger.warning("No active Neo4j connection, attempting to reconnect")
                if not self.connect():
                    NEO4J_QUERIES_TOTAL.labels(
                        query_type=query_type, status="error"
                    ).inc()
                    return []

            with self.driver.session() as session:
                result = session.run(query, params)
                records = [record.data() for record in result]

            # Record success metrics
            NEO4J_QUERIES_TOTAL.labels(query_type=query_type, status="success").inc()
            query_duration = time.time() - start_time
            NEO4J_QUERY_DURATION.labels(query_type=query_type).observe(query_duration)

            # Log latency for significant queries
            if query_duration > 0.1:  # Log queries taking more than 100ms
                logger.warning(
                    f"Slow Neo4j query ({query_duration:.3f}s): {query_type}"
                )

            return records

        except Exception as e:
            # Record failure metrics
            NEO4J_QUERIES_TOTAL.labels(query_type=query_type, status="error").inc()
            query_duration = time.time() - start_time
            NEO4J_QUERY_DURATION.labels(query_type=query_type).observe(query_duration)

            logger.error(f"Neo4j query error ({query_type}): {e}")
            return []

    def _is_connected(self) -> bool:
        """Check if the connection to Neo4j is active."""
        try:
            with self.driver.session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception:
            return False

    def create_indices(self) -> None:
        """Create necessary indices in Neo4j for performance."""
        # Base indices for Card and IP nodes
        self.run(
            "CREATE INDEX IF NOT EXISTS FOR (c:Card) ON (c.id)",
            query_type="create_index",
        )
        self.run(
            "CREATE INDEX IF NOT EXISTS FOR (i:IP) ON (i.addr)",
            query_type="create_index",
        )

        # Composite indices for Device and Merchant
        self.run(
            "CREATE INDEX IF NOT EXISTS FOR (d:Device) ON (d.id)",
            query_type="create_index",
        )
        self.run(
            "CREATE INDEX IF NOT EXISTS FOR (d:Device) ON (d.fp_hash)",
            query_type="create_index",
        )
        self.run(
            "CREATE INDEX IF NOT EXISTS FOR (m:Merchant) ON (m.id)",
            query_type="create_index",
        )

        logger.info("Created Neo4j indices for Card, IP, Device, and Merchant nodes")
