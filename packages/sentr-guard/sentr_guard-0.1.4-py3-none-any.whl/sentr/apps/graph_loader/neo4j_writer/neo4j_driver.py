"""
Neo4j driver for Graph Loader service.

Handles high-performance batch writes to Neo4j with circuit breaker and retry logic.
"""

import threading
import time
from collections import deque
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog
from neo4j import Driver, GraphDatabase
from neo4j.exceptions import ClientError, ServiceUnavailable, TransientError

from apps.graph_loader.config import config

logger = structlog.get_logger()


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Circuit breaker for Neo4j operations to handle failures gracefully.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_timeout: int = 5,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            half_open_timeout: Time to wait in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_timeout = half_open_timeout

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = time.time()

        self._lock = threading.RLock()

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker transitioning to half-open")
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception:
                self._on_failure()
                raise

    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.last_success_time = time.time()
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker closed after successful operation")

    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                "Circuit breaker opened due to failures",
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
            )

    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self.state == CircuitBreakerState.OPEN


class Neo4jBatchWriter:
    """
    High-performance Neo4j batch writer with circuit breaker and retry logic.

    Features:
    - Batch UNWIND operations for efficiency
    - Circuit breaker for fault tolerance
    - Exponential backoff retry
    - Connection pooling
    - Performance monitoring
    """

    def __init__(self):
        """Initialize Neo4j batch writer."""
        self.config = config["neo4j"]
        self.driver: Optional[Driver] = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config["circuit_breaker"]["failure_threshold"],
            recovery_timeout=self.config["circuit_breaker"]["recovery_timeout"],
            half_open_timeout=self.config["circuit_breaker"]["half_open_timeout"],
        )

        # Performance tracking
        self.write_times = deque(maxlen=100)
        self.total_edges_written = 0
        self.total_batches_written = 0
        self.last_write_time = 0

        # Batch settings
        self.batch_size = self.config["batch_size"]
        self.batch_timeout_ms = self.config["batch_timeout_ms"]

        self._lock = threading.RLock()

    def connect(self):
        """Establish connection to Neo4j."""
        try:
            logger.info("Connecting to Neo4j", uri=self.config["uri"])

            self.driver = GraphDatabase.driver(
                self.config["uri"],
                auth=(self.config["username"], self.config["password"]),
                max_connection_lifetime=self.config["max_connection_lifetime"],
                max_connection_pool_size=self.config["max_connection_pool_size"],
                connection_acquisition_timeout=self.config[
                    "connection_acquisition_timeout"
                ],
                encrypted=self.config["encrypted"],
                trust=self.config["trust"],
            )

            # Test connection
            with self.driver.session(database=self.config["database"]) as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value != 1:
                    raise Exception("Connection test failed")

            logger.info("Successfully connected to Neo4j")

            # Initialize schema
            self._initialize_schema()

        except Exception as e:
            logger.error("Failed to connect to Neo4j", error=str(e))
            raise

    def _initialize_schema(self):
        """Initialize Neo4j schema with constraints and indexes."""
        schema_queries = [
            # Constraints for uniqueness
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT card_id IF NOT EXISTS FOR (c:Card) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT ip_id IF NOT EXISTS FOR (i:IP) REQUIRE i.id IS UNIQUE",
            "CREATE CONSTRAINT merchant_id IF NOT EXISTS FOR (m:Merchant) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT device_id IF NOT EXISTS FOR (d:Device) REQUIRE d.id IS UNIQUE",
            # Indexes for performance
            "CREATE INDEX edge_id_index IF NOT EXISTS FOR ()-[r]-() ON (r.edge_id)",
            "CREATE INDEX edge_timestamp_index IF NOT EXISTS FOR ()-[r]-() ON (r.first_seen)",
            "CREATE INDEX edge_bucket_index IF NOT EXISTS FOR ()-[r]-() ON (r.bucket_timestamp)",
        ]

        try:
            with self.driver.session(database=self.config["database"]) as session:
                created_elements = []
                failed_elements = []

                for query in schema_queries:
                    try:
                        session.run(query)
                        created_elements.append(
                            query.split()[2]
                        )  # Extract element name
                        logger.debug("Executed schema query", query=query)
                    except ClientError as e:
                        if (
                            "already exists" in str(e).lower()
                            or "equivalent" in str(e).lower()
                        ):
                            created_elements.append(
                                query.split()[2]
                            )  # Count as created
                            logger.debug("Schema element already exists", query=query)
                        else:
                            failed_elements.append(query.split()[2])
                            logger.warning(
                                "Schema query failed", query=query, error=str(e)
                            )

                # Validate schema creation
                self._validate_schema_elements(
                    session, created_elements, failed_elements
                )

            logger.info(
                "Schema initialization completed",
                created=len(created_elements),
                failed=len(failed_elements),
            )

        except Exception as e:
            logger.error("Failed to initialize schema", error=str(e))
            # Don't raise - schema issues shouldn't prevent startup

    def _validate_schema_elements(
        self, session, created_elements: List[str], failed_elements: List[str]
    ):
        """Validate that critical schema elements exist."""
        try:
            # Check constraints
            constraints_result = session.run("SHOW CONSTRAINTS")
            existing_constraints = [record["name"] for record in constraints_result]

            # Check indexes
            indexes_result = session.run("SHOW INDEXES")
            existing_indexes = [record["name"] for record in indexes_result]

            # Validate critical elements exist
            critical_elements = ["entity_id", "edge_id_index", "edge_timestamp_index"]
            missing_critical = []

            for element in critical_elements:
                if (
                    element not in existing_constraints
                    and element not in existing_indexes
                ):
                    missing_critical.append(element)

            if missing_critical:
                logger.error(
                    "Critical schema elements missing", missing=missing_critical
                )
            else:
                logger.info(
                    "All critical schema elements validated",
                    constraints=len(existing_constraints),
                    indexes=len(existing_indexes),
                )

        except Exception as e:
            logger.warning("Schema validation failed", error=str(e))

    def write_edges_batch(self, edges: List[Dict[str, Any]]) -> bool:
        """
        Write a batch of edges to Neo4j.

        Args:
            edges: List of edge dictionaries

        Returns:
            True if successful, False otherwise
        """
        if not edges:
            return True

        start_time = time.time()

        try:
            # Use circuit breaker protection
            result = self.circuit_breaker.call(self._write_edges_internal, edges)

            # Track performance
            write_time = time.time() - start_time
            with self._lock:
                self.write_times.append(write_time)
                self.total_edges_written += len(edges)
                self.total_batches_written += 1
                self.last_write_time = time.time()

            logger.debug(
                "Successfully wrote edge batch",
                edge_count=len(edges),
                write_time_ms=round(write_time * 1000, 2),
            )

            return True

        except Exception as e:
            logger.error(
                "Failed to write edge batch",
                error=str(e),
                edge_count=len(edges),
                circuit_breaker_state=self.circuit_breaker.state.value,
            )
            return False

    def _write_edges_internal(self, edges: List[Dict[str, Any]]):
        """Internal method to write edges with retries."""
        if not self.driver:
            raise Exception("Neo4j driver not connected")

        # Build Cypher query for batch UNWIND with typed nodes
        cypher_query = """
        UNWIND $edges AS edge
        
        // Create or get source entity with proper type
        MERGE (src:Entity {id: edge.src})
        ON CREATE SET 
            src.created_at = timestamp(),
            src:Card = CASE WHEN edge.src STARTS WITH 'card:' THEN true ELSE false END,
            src:IP = CASE WHEN edge.src STARTS WITH 'ip:' THEN true ELSE false END,
            src:Merchant = CASE WHEN edge.src STARTS WITH 'merchant:' THEN true ELSE false END,
            src:Device = CASE WHEN edge.src STARTS WITH 'device:' THEN true ELSE false END
        
        // Create or get destination entity with proper type
        MERGE (dst:Entity {id: edge.dst})
        ON CREATE SET 
            dst.created_at = timestamp(),
            dst:Card = CASE WHEN edge.dst STARTS WITH 'card:' THEN true ELSE false END,
            dst:IP = CASE WHEN edge.dst STARTS WITH 'ip:' THEN true ELSE false END,
            dst:Merchant = CASE WHEN edge.dst STARTS WITH 'merchant:' THEN true ELSE false END,
            dst:Device = CASE WHEN edge.dst STARTS WITH 'device:' THEN true ELSE false END
        
        // Create or update relationship
        MERGE (src)-[r:RELATES {edge_id: edge.edge_id}]->(dst)
        ON CREATE SET 
            r.edge_type = edge.edge_type,
            r.first_seen = edge.first_seen,
            r.last_seen = edge.last_seen,
            r.bucket_timestamp = edge.bucket_timestamp,
            r.count = edge.count,
            r.txn_ids = edge.txn_ids,
            r.created_at = timestamp()
        ON MATCH SET 
            r.last_seen = CASE 
                WHEN edge.last_seen > r.last_seen THEN edge.last_seen 
                ELSE r.last_seen 
            END,
            r.count = r.count + edge.count,
            r.txn_ids = CASE 
                WHEN size(r.txn_ids) < 100 THEN r.txn_ids + edge.txn_ids
                ELSE r.txn_ids
            END,
            r.updated_at = timestamp()
            
        // Set additional properties dynamically
        SET r += apoc.map.removeKeys(edge, ['edge_id', 'edge_type', 'src', 'dst', 'first_seen', 'last_seen', 'bucket_timestamp', 'count', 'txn_ids'])
        
        RETURN count(r) as edges_processed
        """

        # Fallback query without APOC (in case APOC is not available)
        fallback_query = """
        UNWIND $edges AS edge
        
        // Create or get source entity with proper type
        MERGE (src:Entity {id: edge.src})
        ON CREATE SET 
            src.created_at = timestamp(),
            src:Card = CASE WHEN edge.src STARTS WITH 'card:' THEN true ELSE false END,
            src:IP = CASE WHEN edge.src STARTS WITH 'ip:' THEN true ELSE false END,
            src:Merchant = CASE WHEN edge.src STARTS WITH 'merchant:' THEN true ELSE false END,
            src:Device = CASE WHEN edge.src STARTS WITH 'device:' THEN true ELSE false END
        
        // Create or get destination entity with proper type
        MERGE (dst:Entity {id: edge.dst})
        ON CREATE SET 
            dst.created_at = timestamp(),
            dst:Card = CASE WHEN edge.dst STARTS WITH 'card:' THEN true ELSE false END,
            dst:IP = CASE WHEN edge.dst STARTS WITH 'ip:' THEN true ELSE false END,
            dst:Merchant = CASE WHEN edge.dst STARTS WITH 'merchant:' THEN true ELSE false END,
            dst:Device = CASE WHEN edge.dst STARTS WITH 'device:' THEN true ELSE false END
        
        MERGE (src)-[r:RELATES {edge_id: edge.edge_id}]->(dst)
        ON CREATE SET 
            r.edge_type = edge.edge_type,
            r.first_seen = edge.first_seen,
            r.last_seen = edge.last_seen,
            r.bucket_timestamp = edge.bucket_timestamp,
            r.count = edge.count,
            r.txn_ids = edge.txn_ids,
            r.created_at = timestamp()
        ON MATCH SET 
            r.last_seen = CASE 
                WHEN edge.last_seen > r.last_seen THEN edge.last_seen 
                ELSE r.last_seen 
            END,
            r.count = r.count + edge.count,
            r.updated_at = timestamp()
            
        RETURN count(r) as edges_processed
        """

        retry_count = 0
        max_retries = self.config["retry_attempts"]

        while retry_count <= max_retries:
            try:
                with self.driver.session(database=self.config["database"]) as session:
                    # Try with APOC first, fallback to basic query
                    try:
                        result = session.run(cypher_query, edges=edges)
                        summary = result.consume()
                        return summary
                    except ClientError as e:
                        if "apoc" in str(e).lower():
                            logger.debug("APOC not available, using fallback query")
                            result = session.run(fallback_query, edges=edges)
                            summary = result.consume()
                            return summary
                        else:
                            raise

            except (ServiceUnavailable, TransientError) as e:
                retry_count += 1
                if retry_count <= max_retries:
                    wait_time = min(
                        self.config["retry_delay_ms"]
                        * (2 ** (retry_count - 1))
                        / 1000.0,
                        30.0,  # Max 30 seconds
                    )
                    logger.warning(
                        "Neo4j write failed, retrying",
                        error=str(e),
                        retry_count=retry_count,
                        max_retries=max_retries,
                        wait_time=wait_time,
                    )
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                logger.error("Unexpected error in Neo4j write", error=str(e))
                raise

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            if not self.write_times:
                return {
                    "avg_write_time_ms": 0,
                    "p95_write_time_ms": 0,
                    "total_edges_written": self.total_edges_written,
                    "total_batches_written": self.total_batches_written,
                    "edges_per_second": 0,
                    "circuit_breaker_state": self.circuit_breaker.state.value,
                }

            sorted_times = sorted(self.write_times)
            avg_time = sum(self.write_times) / len(self.write_times)
            p95_time = sorted_times[int(len(sorted_times) * 0.95)]

            # Calculate edges per second over last minute
            current_time = time.time()
            recent_window = 60  # seconds
            if current_time - self.last_write_time < recent_window:
                edges_per_second = self.total_edges_written / recent_window
            else:
                edges_per_second = 0

            return {
                "avg_write_time_ms": round(avg_time * 1000, 2),
                "p95_write_time_ms": round(p95_time * 1000, 2),
                "total_edges_written": self.total_edges_written,
                "total_batches_written": self.total_batches_written,
                "edges_per_second": round(edges_per_second, 2),
                "circuit_breaker_state": self.circuit_breaker.state.value,
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Neo4j connection."""
        try:
            if not self.driver:
                return {"status": "unhealthy", "error": "Driver not connected"}

            with self.driver.session(database=self.config["database"]) as session:
                start_time = time.time()
                result = session.run("RETURN 1 as health_check")
                health_value = result.single()["health_check"]
                response_time = time.time() - start_time

                if health_value == 1:
                    return {
                        "status": "healthy",
                        "response_time_ms": round(response_time * 1000, 2),
                        "circuit_breaker_state": self.circuit_breaker.state.value,
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": "Health check returned unexpected value",
                    }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            try:
                self.driver.close()
                logger.info("Neo4j driver closed")
            except Exception as e:
                logger.error("Error closing Neo4j driver", error=str(e))
