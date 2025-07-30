"""
Edge builder for Graph Loader service.

Converts transaction data into graph edges based on configurable rules.
"""

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog

from apps.graph_loader.config import config, get_edge_config, get_enabled_edge_types

logger = structlog.get_logger()


@dataclass
class Edge:
    """Represents a graph edge with all necessary properties."""

    edge_type: str
    src: str
    dst: str
    edge_id: str
    timestamp: int
    bucket_timestamp: int
    properties: Dict[str, Any]
    txn_id: str


class EdgeBuilder:
    """
    High-performance edge builder that converts transactions into graph edges.

    Features:
    - Configurable edge type rules
    - Time-bucketed edge aggregation
    - Efficient edge ID generation
    - Property extraction and validation
    """

    def __init__(self):
        """Initialize edge builder with configuration."""
        self.enabled_edge_types = get_enabled_edge_types()
        self.time_bucket_size = config["edge_processing"]["time_bucket_size"]
        self.max_txn_ids = config["edge_processing"]["max_txn_ids"]

        logger.info(
            "Initialized edge builder",
            enabled_edge_types=self.enabled_edge_types,
            time_bucket_size=self.time_bucket_size,
        )

    def build_edges(self, transactions: List[Dict[str, Any]]) -> List[Edge]:
        """
        Build edges from a batch of transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of Edge objects
        """
        edges = []

        for transaction in transactions:
            try:
                # Extract transaction metadata
                txn_id = transaction.get(
                    "transaction_id", transaction.get("id", "unknown")
                )
                timestamp = self._extract_timestamp(transaction)
                bucket_timestamp = self._get_bucket_timestamp(timestamp)

                # Build edges for each enabled edge type
                for edge_type in self.enabled_edge_types:
                    edge = self._build_edge(
                        transaction, edge_type, txn_id, timestamp, bucket_timestamp
                    )
                    if edge:
                        edges.append(edge)

            except Exception as e:
                logger.error(
                    "Error building edges for transaction",
                    error=str(e),
                    transaction_id=transaction.get("transaction_id", "unknown"),
                )

        return edges

    def _extract_timestamp(self, transaction: Dict[str, Any]) -> int:
        """Extract timestamp from transaction."""
        # Try multiple timestamp fields
        timestamp_fields = [
            "timestamp",
            "created_at",
            "processed_at",
            "_kafka_metadata.timestamp",
        ]

        for field in timestamp_fields:
            if "." in field:
                # Handle nested fields like '_kafka_metadata.timestamp'
                value = transaction
                for part in field.split("."):
                    value = value.get(part, {})
                    if not isinstance(value, dict) and part != field.split(".")[-1]:
                        value = {}
                        break
                if value and isinstance(value, (int, float)):
                    return int(value)
            else:
                value = transaction.get(field)
                if value and isinstance(value, (int, float)):
                    return int(value)

        # Fallback to current time
        logger.warning("No valid timestamp found in transaction, using current time")
        return int(time.time())

    def _get_bucket_timestamp(self, timestamp: int) -> int:
        """Get bucketed timestamp for edge aggregation."""
        return (timestamp // self.time_bucket_size) * self.time_bucket_size

    def _build_edge(
        self,
        transaction: Dict[str, Any],
        edge_type: str,
        txn_id: str,
        timestamp: int,
        bucket_timestamp: int,
    ) -> Optional[Edge]:
        """Build a single edge from transaction data."""
        edge_config = get_edge_config(edge_type)
        if not edge_config:
            logger.warning("No configuration found for edge type", edge_type=edge_type)
            return None

        try:
            # Extract source and destination
            src_value = transaction.get(edge_config["src_field"])
            dst_value = transaction.get(edge_config["dst_field"])

            if not src_value or not dst_value:
                logger.debug(
                    "Missing source or destination for edge",
                    edge_type=edge_type,
                    src_field=edge_config["src_field"],
                    dst_field=edge_config["dst_field"],
                    src_value=src_value,
                    dst_value=dst_value,
                )
                return None

            # Build source and destination IDs with prefixes
            src = f"{edge_config['src_prefix']}{src_value}"
            dst = f"{edge_config['dst_prefix']}{dst_value}"

            # Extract properties first
            properties = self._extract_properties(
                transaction, edge_config.get("properties", [])
            )

            # Generate edge ID for idempotency including critical properties
            edge_id = self._generate_edge_id(
                edge_type, src, dst, bucket_timestamp, properties
            )

            return Edge(
                edge_type=edge_type,
                src=src,
                dst=dst,
                edge_id=edge_id,
                timestamp=timestamp,
                bucket_timestamp=bucket_timestamp,
                properties=properties,
                txn_id=txn_id,
            )

        except Exception as e:
            logger.error(
                "Error building edge",
                error=str(e),
                edge_type=edge_type,
                transaction_id=txn_id,
            )
            return None

    def _generate_edge_id(
        self,
        edge_type: str,
        src: str,
        dst: str,
        bucket_timestamp: int,
        properties: Dict[str, Any] = None,
    ) -> str:
        """Generate deterministic edge ID for idempotency including critical properties."""
        # Include critical properties in hash to prevent property overwrites
        properties = properties or {}

        # Extract critical properties that affect edge identity
        amount = str(properties.get("amount", ""))
        is_success = str(properties.get("is_success", ""))

        # Create hash input from edge components including critical properties
        hash_input = f"{edge_type}:{src}:{dst}:{bucket_timestamp}:{amount}:{is_success}"

        # Generate SHA-256 hash and take first 16 characters
        hash_object = hashlib.sha256(hash_input.encode())
        return hash_object.hexdigest()[:16]

    def _extract_properties(
        self, transaction: Dict[str, Any], property_fields: List[str]
    ) -> Dict[str, Any]:
        """Extract properties from transaction based on configuration."""
        properties = {}

        for field in property_fields:
            value = transaction.get(field)
            if value is not None:
                # Convert to appropriate type and sanitize
                properties[field] = self._sanitize_property_value(value)

        return properties

    def _sanitize_property_value(self, value: Any) -> Any:
        """Sanitize property value for Neo4j storage."""
        # Handle different data types
        if isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, list):
            # Convert lists to comma-separated strings (Neo4j arrays can be complex)
            return ",".join(str(v) for v in value[:10])  # Limit to 10 items
        elif isinstance(value, dict):
            # Convert dicts to JSON strings
            import json

            try:
                return json.dumps(value)[:500]  # Limit size
            except:
                return str(value)[:500]
        else:
            # Convert everything else to string
            return str(value)[:500]  # Limit string length


class EdgeAggregator:
    """
    Aggregates edges by edge_id to reduce database writes.

    Combines multiple edges with the same edge_id into a single edge
    with aggregated properties and transaction lists.
    """

    def __init__(self):
        """Initialize edge aggregator."""
        self.max_txn_ids = config["edge_processing"]["max_txn_ids"]

    def aggregate_edges(self, edges: List[Edge]) -> List[Dict[str, Any]]:
        """
        Aggregate edges by edge_id.

        Args:
            edges: List of Edge objects

        Returns:
            List of aggregated edge dictionaries ready for Neo4j
        """
        edge_groups = {}

        # Group edges by edge_id
        for edge in edges:
            if edge.edge_id not in edge_groups:
                edge_groups[edge.edge_id] = {
                    "edge_type": edge.edge_type,
                    "src": edge.src,
                    "dst": edge.dst,
                    "edge_id": edge.edge_id,
                    "first_seen": edge.timestamp,
                    "last_seen": edge.timestamp,
                    "bucket_timestamp": edge.bucket_timestamp,
                    "count": 0,
                    "txn_ids": [],
                    "properties": {},
                }

            group = edge_groups[edge.edge_id]

            # Update aggregated values
            group["first_seen"] = min(group["first_seen"], edge.timestamp)
            group["last_seen"] = max(group["last_seen"], edge.timestamp)
            group["count"] += 1

            # Add transaction ID (with limit)
            if len(group["txn_ids"]) < self.max_txn_ids:
                group["txn_ids"].append(edge.txn_id)

            # Merge properties (simple strategy: last value wins)
            group["properties"].update(edge.properties)

        return list(edge_groups.values())

    def format_for_neo4j(
        self, aggregated_edges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format aggregated edges for Neo4j batch write.

        Args:
            aggregated_edges: List of aggregated edge dictionaries

        Returns:
            List of edges formatted for Neo4j UNWIND operation
        """
        formatted_edges = []

        for edge in aggregated_edges:
            # Create Neo4j-compatible edge record
            neo4j_edge = {
                "edge_id": edge["edge_id"],
                "edge_type": edge["edge_type"],
                "src": edge["src"],
                "dst": edge["dst"],
                "first_seen": edge["first_seen"],
                "last_seen": edge["last_seen"],
                "bucket_timestamp": edge["bucket_timestamp"],
                "count": edge["count"],
                "txn_ids": edge["txn_ids"],
                # Flatten properties into the main record
                **edge["properties"],
            }

            formatted_edges.append(neo4j_edge)

        return formatted_edges
