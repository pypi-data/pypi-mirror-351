"""
Decision Engine for fraud detection.

Coordinates feature store lookup, rule evaluation, and optional ML scoring
to produce final fraud detection verdicts.
"""

import asyncio
import time
from typing import Any, Dict, Optional

import structlog
from prometheus_client import Counter, Histogram

from common.enums import PanicMode, PanicReason
from feature_store import PaymentAttempt
from feature_store.redis_store import RedisFeatureStore
from rules import RuleAction, RuleSet, load_ruleset_from_yaml

from .verdict import Verdict

# Prometheus metrics
DECISION_LATENCY = Histogram(
    "decision_latency_seconds",
    "Decision engine latency",
    buckets=[0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1],
)

DECISIONS_TOTAL = Counter(
    "decisions_total", "Total decisions made", ["decision", "source"]
)

PANIC_MODE_TOTAL = Counter("panic_mode_total", "Total panic mode activations", ["mode"])

# Logger
logger = structlog.get_logger(__name__)


class RedisUnavailableError(Exception):
    """Raised when Redis is unavailable and should block transactions."""

    pass


class DecisionEngine:
    """
    Main decision engine that coordinates all fraud detection components.

    Handles panic modes, feature lookup, rule evaluation, and optional ML scoring.
    """

    def __init__(
        self,
        feature_store: RedisFeatureStore,
        ruleset: RuleSet,
        redis_client,
        graph_client=None,
        enable_graph: bool = False,
    ):
        """
        Initialize decision engine.

        Args:
            feature_store: Redis-based feature store
            ruleset: Compiled rule set for evaluation
            redis_client: Redis client for panic mode checks
            graph_client: Optional ML graph client
            enable_graph: Whether to enable ML graph scoring
        """
        self.feature_store = feature_store
        self.ruleset = ruleset
        self.redis_client = redis_client
        self.graph_client = graph_client
        self.enable_graph = enable_graph

        logger.info(
            "Decision engine initialized",
            rules_count=len(ruleset.rules),
            enable_graph=enable_graph,
            revision=ruleset.revision_hash,
        )

    async def score(self, event: PaymentAttempt) -> Verdict:
        """
        Score a payment attempt and return fraud detection verdict.

        Args:
            event: Payment attempt to evaluate

        Returns:
            Verdict with decision, score, and reasons
        """
        start_time = time.perf_counter()
        logger.info(f"Starting decision scoring for event: {event.merchant_id}")

        # Quick Redis health check first - if Redis is down, block immediately
        try:
            logger.error("Testing Redis connectivity before processing")
            await asyncio.wait_for(
                self.redis_client.ping(), timeout=0.1
            )  # 100ms timeout
            logger.error("Redis connectivity OK")
        except Exception as e:
            logger.error(
                "Redis health check failed", error=str(e), error_type=type(e).__name__
            )
            # Redis is unavailable - return blocking verdict immediately
            return Verdict(
                decision="block",
                score=1.0,
                reasons=("redis_unavailable",),
                revision=self.ruleset.revision_hash,
            )

        try:
            # Check panic mode first (fast path)
            logger.info("Checking panic mode...")
            try:
                panic_verdict = await self._check_panic_mode(event)
                if panic_verdict:
                    logger.info(f"DEBUG: Panic mode verdict: {panic_verdict.decision}")
                    return panic_verdict
                logger.info("DEBUG: No panic mode, continuing with normal flow")
            except RedisUnavailableError as e:
                logger.warning(
                    f"DEBUG: RedisUnavailableError caught in score method: {e}"
                )
                # Re-raise to propagate to middleware
                raise
            except Exception as e:
                logger.error(f"DEBUG: Unexpected error in panic mode check: {e}")
                # For non-Redis errors, continue with normal flow
                pass

            # Get features from feature store
            features = await self._compute_features_for_event(event)

            # Evaluate rules
            rule_hits = self.ruleset.evaluate(features)

            # Determine rule-based verdict
            rule_verdict = self._evaluate_rule_hits(rule_hits)
            logger.info(f"DEBUG: Rule verdict: {rule_verdict.decision}")

            # Optional ML graph scoring
            if self.enable_graph and self.graph_client and not rule_verdict.is_blocking:
                try:
                    graph_score = await asyncio.wait_for(
                        self.graph_client.score(event), timeout=0.05  # 50ms timeout
                    )

                    # Combine rule and graph verdicts
                    final_verdict = self._combine_verdicts(rule_verdict, graph_score)
                    DECISIONS_TOTAL.labels(
                        decision=final_verdict.decision, source="combined"
                    ).inc()

                except asyncio.TimeoutError:
                    logger.warning("Graph client timeout, using rules-only verdict")
                    final_verdict = rule_verdict
                    DECISIONS_TOTAL.labels(
                        decision=final_verdict.decision, source="rules_timeout"
                    ).inc()
                except Exception as e:
                    logger.error(
                        "Graph client error, using rules-only verdict", error=str(e)
                    )
                    final_verdict = rule_verdict
                    DECISIONS_TOTAL.labels(
                        decision=final_verdict.decision, source="rules_error"
                    ).inc()
            else:
                final_verdict = rule_verdict
                DECISIONS_TOTAL.labels(
                    decision=final_verdict.decision, source="rules_only"
                ).inc()

            # Log decision
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Decision made",
                merchant_id=event.merchant_id,
                decision=final_verdict.decision,
                score=final_verdict.score,
                reasons=final_verdict.reasons,
                latency_ms=round(latency_ms, 2),
                revision=final_verdict.revision,
            )

            logger.info(f"DEBUG: Returning final verdict: {final_verdict.decision}")
            return final_verdict

        except RedisUnavailableError as e:
            logger.warning(
                f"DEBUG: RedisUnavailableError propagating from score method: {e}"
            )
            # Re-raise to middleware
            raise
        except Exception as e:
            logger.error(
                f"DEBUG: Unexpected error in score method: {type(e).__name__}: {e}"
            )
            # For unexpected errors, return a safe verdict
            return Verdict(
                decision="allow",
                score=0.0,
                reasons=("engine_error",),
                revision=self.ruleset.revision_hash,
            )
        finally:
            # Record latency metric
            DECISION_LATENCY.observe(time.perf_counter() - start_time)

    async def _check_panic_mode(self, event: PaymentAttempt) -> Optional[Verdict]:
        """
        Check for panic mode flags in Redis.

        Args:
            event: Payment attempt (for logging context)

        Returns:
            Panic verdict if panic mode is active, None otherwise
        """
        try:
            logger.info(
                f"DEBUG: About to check Redis panic mode for {event.merchant_id}"
            )
            # Check for panic modes with single Redis call
            panic_mode = await self.redis_client.get("panic")
            logger.info(
                f"Panic mode check: key='{panic_mode}', type={type(panic_mode)}"
            )

            # Handle bytes returned by redis.asyncio
            if panic_mode:
                panic_str = (
                    panic_mode.decode("utf-8")
                    if isinstance(panic_mode, bytes)
                    else panic_mode
                )

                if panic_str == PanicMode.BLOCK_ALL:
                    PANIC_MODE_TOTAL.labels(mode="block_all").inc()
                    logger.warning(
                        "Panic mode: blocking all transactions",
                        merchant_id=event.merchant_id,
                    )
                    return Verdict(
                        decision="block",
                        score=1.0,
                        reasons=(PanicReason.PANIC_BLOCK_ALL,),
                        revision=self.ruleset.revision_hash,
                    )

                elif panic_str == PanicMode.ALLOW_ALL:
                    PANIC_MODE_TOTAL.labels(mode="allow_all").inc()
                    logger.warning(
                        "Panic mode: allowing all transactions",
                        merchant_id=event.merchant_id,
                    )
                    return Verdict(
                        decision="allow",
                        score=0.0,
                        reasons=(PanicReason.PANIC_ALLOW_ALL,),
                        revision=self.ruleset.revision_hash,
                    )

            logger.info("DEBUG: No panic mode active, returning None")
            return None

        except Exception as e:
            logger.error("Failed to check panic mode", error=str(e))
            logger.error(
                "Redis error details",
                exception_type=type(e).__name__,
                exception_module=type(e).__module__,
            )
            # Check if this is a Redis connection error
            error_str = str(e).lower()
            logger.error("Error analysis", error_string=error_str)
            is_redis_error = (
                "redis" in error_str
                or "connection" in error_str
                or "timeout" in error_str
                or "name or service not known" in error_str
            )
            logger.error("Redis error check", is_redis_error=is_redis_error)
            if is_redis_error:
                # Redis is unavailable - raise exception to trigger 402 response
                logger.error("Raising RedisUnavailableError for middleware")
                raise RedisUnavailableError(
                    f"Redis unavailable during panic mode check: {e}"
                )
            # For other errors, fail open - don't block on non-Redis errors
            logger.error("Not a Redis error, failing open")
            return None

    def _evaluate_rule_hits(self, rule_hits) -> Verdict:
        """
        Convert rule hits into a verdict.

        Args:
            rule_hits: List of rules that triggered

        Returns:
            Verdict based on rule evaluation
        """
        if not rule_hits:
            # No rules triggered - allow
            return Verdict(
                decision="allow",
                score=0.0,
                reasons=(),
                revision=self.ruleset.revision_hash,
            )

        # Find highest scoring rule and determine action
        max_score = max(rule.score for rule in rule_hits)
        rule_ids = tuple(rule.id for rule in rule_hits)

        # Determine decision based on rule actions
        # Priority: block > challenge_3ds > allow
        has_block = any(rule.action == RuleAction.BLOCK for rule in rule_hits)
        has_challenge = any(
            rule.action == RuleAction.CHALLENGE_3DS for rule in rule_hits
        )

        if has_block:
            decision = "block"
        elif has_challenge:
            decision = "challenge_3ds"
        else:
            decision = "allow"

        return Verdict(
            decision=decision,
            score=max_score,
            reasons=rule_ids,
            revision=self.ruleset.revision_hash,
        )

    async def _compute_features_for_event(
        self, event: PaymentAttempt
    ) -> Dict[str, Any]:
        """
        Compute features for a payment attempt.

        Args:
            event: Payment attempt to compute features for

        Returns:
            Dictionary of computed features
        """
        # Basic features from the event itself
        features = {
            "merchant_id": event.merchant_id,
            "amount": event.amount,
            "ip": event.ip,
            "bin": event.bin,
            "timestamp": event.ts,
        }

        # Try to get additional features from feature store
        try:
            feature_names = [
                "fail_rate_60s",
                "attempts_60s",
                "velocity_1h",
                "country_code",
            ]
            response = await self.feature_store.get_features(
                entity_id=event.ip,
                feature_names=feature_names,  # Use IP as entity for now
            )

            # Merge additional features
            features.update(response.features)

        except Exception as e:
            logger.warning("Failed to get additional features from store", error=str(e))

        return features

    def _combine_verdicts(self, rule_verdict: Verdict, graph_score: float) -> Verdict:
        """
        Combine rule-based verdict with ML graph score.

        Args:
            rule_verdict: Verdict from rule evaluation
            graph_score: ML model score (0.0-1.0)

        Returns:
            Combined verdict
        """
        # Use higher score and combine reasons
        if graph_score > rule_verdict.score:
            # Graph score is higher
            if graph_score >= 0.8:
                decision = "block"
            elif graph_score >= 0.5:
                decision = "challenge_3ds"
            else:
                decision = rule_verdict.decision

            return Verdict(
                decision=decision,
                score=graph_score,
                reasons=rule_verdict.reasons + ("graph_ml",),
                revision=rule_verdict.revision,
            )
        else:
            # Rule verdict is higher or equal
            return rule_verdict

    @classmethod
    async def create(
        cls,
        redis_url: str,
        rules_path: str,
        enable_graph: bool = False,
        graph_client=None,
    ) -> "DecisionEngine":
        """
        Factory method to create decision engine with dependencies.

        Args:
            redis_url: Redis connection URL
            rules_path: Path to rules YAML file
            enable_graph: Whether to enable ML graph scoring
            graph_client: Optional ML graph client

        Returns:
            Configured decision engine
        """
        import redis.asyncio as redis

        # Initialize Redis client
        redis_client = redis.from_url(redis_url)

        # Initialize feature store
        feature_store = RedisFeatureStore()

        # Load ruleset
        ruleset = load_ruleset_from_yaml(rules_path)

        return cls(
            feature_store=feature_store,
            ruleset=ruleset,
            redis_client=redis_client,
            graph_client=graph_client,
            enable_graph=enable_graph,
        )
