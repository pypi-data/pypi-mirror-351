"""
TorchServe handler for fraud detection model serving.
Handles feature extraction, model inference, and response formatting.
"""

import json
import logging
import os
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import redis
import torch
from prometheus_client import Counter, Gauge, Histogram, Summary

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get edge types configuration
ACTIVE_EDGES = set(os.getenv("ACTIVE_EDGES", "card_ip").split(","))
logger.info(f"Model initialized with active edge types: {ACTIVE_EDGES}")

# Prometheus metrics
MODEL_PREDICTION_TIME = Summary(
    "model_prediction_seconds", "Time spent on model prediction"
)
FEATURE_EXTRACTION_TIME = Summary(
    "feature_extraction_seconds", "Time spent on feature extraction"
)
NEO4J_QUERY_TIME = Histogram(
    "neo4j_query_seconds", "Time spent on Neo4j queries", ["query_type"]
)
CACHE_HIT_RATIO = Gauge(
    "subgraph_cache_hit_ratio", "Cache hit ratio for subgraph cache"
)
PREDICTIONS_TOTAL = Counter(
    "predictions_total", "Total number of predictions made", ["status", "risk_level"]
)
REDIS_FEATURES_FOUND = Counter(
    "redis_features_found", "Count of feature keys found in Redis", ["feature_type"]
)
REDIS_FEATURES_MISSING = Counter(
    "redis_features_missing", "Count of feature keys missing in Redis", ["feature_type"]
)


class SubgraphCache:
    """LRU cache for storing recently accessed card subgraphs."""

    def __init__(self, max_size: int = 10000, ttl: int = 30):
        """Initialize the subgraph cache."""
        self.cache = {}  # {card_id: (graph_data, timestamp)}
        self.max_size = max_size
        self.ttl_seconds = ttl
        self.hits = 0
        self.misses = 0

    def get(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get subgraph data for a card if it exists and is not expired."""
        if card_id in self.cache:
            data, timestamp = self.cache[card_id]
            if time.time() - timestamp <= self.ttl_seconds:
                self.hits += 1
                # Update hit ratio metric
                if self.hits + self.misses > 0:
                    CACHE_HIT_RATIO.set(self.hits / (self.hits + self.misses))
                return data
            else:
                # Expired entry
                del self.cache[card_id]

        self.misses += 1
        # Update hit ratio metric
        if self.hits + self.misses > 0:
            CACHE_HIT_RATIO.set(self.hits / (self.hits + self.misses))
        return None

    def put(self, card_id: str, data: Dict[str, Any]) -> None:
        """Add or update subgraph data for a card."""
        # If cache is full, remove oldest entry
        if len(self.cache) >= self.max_size and card_id not in self.cache:
            oldest_card = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_card]

        # Add or update cache entry
        self.cache[card_id] = (data, time.time())


class FraudDetectionHandler:
    """Handler for fraud detection model serving."""

    def __init__(self):
        """Initialize the handler."""
        self.initialized = False
        self.model = None
        self.redis_client = None
        self.neo4j_client = None
        self.device = None
        self.subgraph_cache = SubgraphCache()

        # Feature configuration
        self.base_features = ["fail_60s", "uniq_ip_60s"]
        self.merchant_features = ["uniq_merchant_60s"]
        self.device_features = ["uniq_device_60s"]

        logger.info("FraudDetectionHandler initialized")

    def initialize(self, context):
        """
        Initialize model and connections.
        Called once at model loading time.
        """
        try:
            properties = context.system_properties
            model_dir = properties.get("model_dir")
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # Load the model
            model_path = os.path.join(model_dir, "fraud_model.pt")
            self.model = torch.jit.load(model_path, map_location=self.device)
            self.model.eval()

            # Initialize Redis client
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            self.redis_client = redis.Redis(
                host=redis_host, port=redis_port, decode_responses=True
            )

            # Initialize Neo4j client if needed for graph features
            if ACTIVE_EDGES - {"card_ip"}:  # If we have more than just card_ip
                # Lazy import Neo4j client to avoid loading it when not needed
                from neo4j import GraphDatabase

                neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
                neo4j_user = os.getenv("NEO4J_USER", "neo4j")
                neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

                self.neo4j_client = GraphDatabase.driver(
                    neo4j_uri, auth=(neo4j_user, neo4j_password)
                )
                logger.info(f"Connected to Neo4j at {neo4j_uri}")

            self.initialized = True
            logger.info(f"Model loaded successfully on {self.device}")

        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            traceback.print_exc()
            raise

    @FEATURE_EXTRACTION_TIME.time()
    def extract_features(self, card_id: str, merchant_id: str = None) -> np.ndarray:
        """
        Extract features for the given card and merchant IDs.

        Args:
            card_id: Card identifier
            merchant_id: Optional merchant identifier

        Returns:
            Feature vector as numpy array
        """
        # Build the Redis key for card features
        card_key = f"card:{card_id}"

        # Get base features from Redis
        feat_vec = []
        for feat in self.base_features:
            value = self.redis_client.hget(card_key, feat)
            if value is not None:
                REDIS_FEATURES_FOUND.labels(feature_type=feat).inc()
                feat_vec.append(float(value))
            else:
                REDIS_FEATURES_MISSING.labels(feature_type=feat).inc()
                feat_vec.append(0.0)

        # Get merchant edge features if enabled
        if "card_merchant" in ACTIVE_EDGES:
            for feat in self.merchant_features:
                value = self.redis_client.hget(card_key, feat)
                if value is not None:
                    REDIS_FEATURES_FOUND.labels(feature_type=feat).inc()
                    feat_vec.append(float(value))
                else:
                    REDIS_FEATURES_MISSING.labels(feature_type=feat).inc()
                    feat_vec.append(0.0)

        # Get device edge features if enabled
        if "card_device" in ACTIVE_EDGES:
            for feat in self.device_features:
                value = self.redis_client.hget(card_key, feat)
                if value is not None:
                    REDIS_FEATURES_FOUND.labels(feature_type=feat).inc()
                    feat_vec.append(float(value))
                else:
                    REDIS_FEATURES_MISSING.labels(feature_type=feat).inc()
                    feat_vec.append(0.0)

        return np.array(feat_vec, dtype=np.float32)

    def fetch_card_subgraph(self, card_id: str) -> Dict[str, Any]:
        """
        Fetch the subgraph for a card from Neo4j, using cache if available.

        Args:
            card_id: Card identifier

        Returns:
            Subgraph data dictionary
        """
        # Check cache first
        cached_data = self.subgraph_cache.get(card_id)
        if cached_data:
            return cached_data

        # Build query based on active edge types
        query_parts = []
        returns = ["card"]

        # Always include card node
        query_parts.append("MATCH (card:Card {id: $card_id})")

        # Add IP relationships if enabled (this is the baseline)
        if "card_ip" in ACTIVE_EDGES:
            query_parts.append("OPTIONAL MATCH (card)-[r_ip:USED_IP]->(ip:IP)")
            returns.extend(["collect(distinct ip) as ips", "collect(r_ip) as ip_rels"])

        # Add merchant relationships if enabled
        if "card_merchant" in ACTIVE_EDGES:
            query_parts.append("OPTIONAL MATCH (card)-[r_m:USED_AT]->(m:Merchant)")
            returns.extend(
                ["collect(distinct m) as merchants", "collect(r_m) as merchant_rels"]
            )

        # Add device relationships if enabled
        if "card_device" in ACTIVE_EDGES:
            query_parts.append("OPTIONAL MATCH (card)-[r_d:USED_DEVICE]->(d:Device)")
            returns.extend(
                ["collect(distinct d) as devices", "collect(r_d) as device_rels"]
            )

        # Build the final query
        query = "\n".join(query_parts) + "\nRETURN " + ", ".join(returns)

        start_time = time.time()
        try:
            with self.neo4j_client.session() as session:
                result = session.run(query, card_id=card_id)
                data = result.single()

                if data:
                    # Process results into a structured dictionary
                    graph_data = {"card": data["card"]}

                    if "card_ip" in ACTIVE_EDGES:
                        graph_data["ips"] = data["ips"]
                        graph_data["ip_relationships"] = data["ip_rels"]

                    if "card_merchant" in ACTIVE_EDGES:
                        graph_data["merchants"] = data["merchants"]
                        graph_data["merchant_relationships"] = data["merchant_rels"]

                    if "card_device" in ACTIVE_EDGES:
                        graph_data["devices"] = data["devices"]
                        graph_data["device_relationships"] = data["device_rels"]

                    # Cache the result
                    self.subgraph_cache.put(card_id, graph_data)
                    return graph_data

                return {"card": None}
        finally:
            # Record query time
            query_time = time.time() - start_time
            NEO4J_QUERY_TIME.labels(query_type="fetch_card_subgraph").observe(
                query_time
            )

    @MODEL_PREDICTION_TIME.time()
    def predict(self, features: np.ndarray) -> Tuple[float, str]:
        """
        Make a fraud prediction using the model.

        Args:
            features: Feature vector as numpy array

        Returns:
            Tuple of (risk_score, risk_level)
        """
        try:
            # Convert features to tensor
            features_tensor = torch.tensor(features, dtype=torch.float32).to(
                self.device
            )

            # Add batch dimension if needed
            if len(features_tensor.shape) == 1:
                features_tensor = features_tensor.unsqueeze(0)

            # Run inference
            with torch.no_grad():
                output = self.model(features_tensor)

            # Get prediction and convert to risk score
            score = output.item()

            # Map score to risk level
            if score < 0.2:
                risk_level = "low"
            elif score < 0.7:
                risk_level = "medium"
            else:
                risk_level = "high"

            # Record prediction metric
            PREDICTIONS_TOTAL.labels(status="success", risk_level=risk_level).inc()

            return score, risk_level

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            # Record prediction error metric
            PREDICTIONS_TOTAL.labels(status="error", risk_level="unknown").inc()
            return 0.0, "error"

    def preprocess(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess the incoming data before model inference.

        Args:
            data: List of request dictionaries

        Returns:
            Processed data ready for inference
        """
        preprocessed_data = []

        for item in data:
            try:
                # Parse input
                input_json = item.get("data")
                if isinstance(input_json, (str, bytes)):
                    input_data = json.loads(input_json)
                else:
                    input_data = input_json

                # Extract key fields
                card_id = input_data.get("card_id")
                merchant_id = input_data.get("merchant_id")

                if not card_id:
                    raise ValueError("Missing required field: card_id")

                # Extract features
                features = self.extract_features(card_id, merchant_id)

                # If we have graph-based features enabled, fetch from Neo4j
                if self.neo4j_client and (ACTIVE_EDGES - {"card_ip"}):
                    # Add graph structure as context, but don't include in features yet
                    # This is for future graph neural network models
                    input_data["graph"] = self.fetch_card_subgraph(card_id)

                # Store processed item
                preprocessed_data.append({"features": features, "context": input_data})

            except Exception as e:
                logger.error(f"Error preprocessing item: {e}")
                preprocessed_data.append(
                    {
                        "features": np.zeros(len(self.base_features), dtype=np.float32),
                        "context": {"error": str(e)},
                        "error": True,
                    }
                )

        return preprocessed_data

    def inference(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run inference on preprocessed data.

        Args:
            data: List of preprocessed data dictionaries

        Returns:
            List of inference results
        """
        results = []

        for item in data:
            try:
                if item.get("error"):
                    # Skip items that had preprocessing errors
                    results.append({"error": item["context"]["error"]})
                    continue

                # Make prediction
                features = item["features"]
                score, risk_level = self.predict(features)

                # Store result
                results.append(
                    {
                        "risk_score": float(score),
                        "risk_level": risk_level,
                        "features_used": len(features),
                    }
                )

            except Exception as e:
                logger.error(f"Error during inference: {e}")
                results.append({"error": str(e)})

        return results

    def postprocess(
        self, inference_output: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Postprocess inference output for response.

        Args:
            inference_output: List of inference result dictionaries

        Returns:
            List of formatted response dictionaries
        """
        postprocessed_output = []

        for result in inference_output:
            try:
                if "error" in result:
                    output = {"status": "error", "error": result["error"]}
                else:
                    output = {
                        "status": "success",
                        "risk_score": result["risk_score"],
                        "risk_level": result["risk_level"],
                        "features_used": result["features_used"],
                        "active_edges": list(ACTIVE_EDGES),
                    }

                postprocessed_output.append(output)

            except Exception as e:
                logger.error(f"Error during postprocessing: {e}")
                postprocessed_output.append(
                    {"status": "error", "error": f"Postprocessing error: {str(e)}"}
                )

        return postprocessed_output

    def handle(self, data, context):
        """
        Handle incoming requests.

        Args:
            data: Input data
            context: Context information

        Returns:
            Response data
        """
        if not self.initialized:
            self.initialize(context)

        # Record request time
        start_time = time.time()

        try:
            if data is None:
                return [{"status": "error", "error": "Empty request"}]

            # Process the request
            preprocessed_data = self.preprocess(data)
            inference_result = self.inference(preprocessed_data)
            response = self.postprocess(inference_result)

            # Add request time to response for debugging
            for resp in response:
                if resp.get("status") == "success":
                    resp["request_time"] = round(time.time() - start_time, 4)

            return response

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return [{"status": "error", "error": str(e)}]


# TorchServe model handler
_service = FraudDetectionHandler()


def handle(data, context):
    """TorchServe handler function."""
    return _service.handle(data, context)
