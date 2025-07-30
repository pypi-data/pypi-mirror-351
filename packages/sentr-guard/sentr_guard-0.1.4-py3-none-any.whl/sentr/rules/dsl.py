"""
Rule DSL (Domain Specific Language) for fraud detection rules.

Provides immutable, slot-based rule definitions with compile-time validation.
Optimized for sub-200µs evaluation performance.
"""

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping

# Valid rule ID pattern: alphanumeric and underscores only (for safe metric labels)
RULE_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")


class RuleAction(str, Enum):
    """Possible actions a rule can take when triggered."""

    BLOCK = "block"
    CHALLENGE_3DS = "challenge_3ds"
    ALLOW = "allow"


class RuleState(str, Enum):
    """Rule execution states for gradual rollout."""

    AUDIT = "audit"  # Log only, don't enforce
    SHADOW = "shadow"  # Evaluate and log, but don't enforce
    ENFORCE = "enforce"  # Full enforcement


@dataclass(slots=True, frozen=True)
class Rule:
    """
    Immutable rule definition for fraud detection.

    Attributes:
        id: Unique rule identifier (alphanumeric + underscore only)
        expr: Expression string to evaluate (transformed to safe AST)
        action: Action to take when rule triggers
        score: Risk score when rule triggers (0.0 to 1.0)
        state: Current state of the rule (audit/shadow/enforce)

    The compiled function is stored separately and not part of equality/hashing.
    """

    id: str
    expr: str
    action: RuleAction
    score: float = 0.9
    state: RuleState = RuleState.AUDIT

    # Compiled evaluation function (populated at load-time)
    # Not part of init, repr, or comparison for immutability
    _fn: Callable[[Mapping[str, Any]], bool] = field(
        init=False, repr=False, compare=False, default=None
    )

    def __post_init__(self):
        """Validate rule fields after initialization."""
        # Validate rule ID format
        if not RULE_ID_PATTERN.match(self.id):
            raise ValueError(
                f"Rule ID '{self.id}' invalid. Must match pattern: {RULE_ID_PATTERN.pattern}"
            )

        # Validate score range
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(
                f"Rule score must be between 0.0 and 1.0, got: {self.score}"
            )

        # Validate expression is not empty
        if not self.expr or not self.expr.strip():
            raise ValueError("Rule expression cannot be empty")

        # Convert string enums to proper enum types if needed
        if isinstance(self.action, str):
            object.__setattr__(self, "action", RuleAction(self.action))
        if isinstance(self.state, str):
            object.__setattr__(self, "state", RuleState(self.state))

    def is_active(self) -> bool:
        """Check if rule is active (not in audit mode)."""
        return self.state != RuleState.AUDIT

    def is_blocking(self) -> bool:
        """Check if rule can block transactions."""
        return self.action in (RuleAction.BLOCK, RuleAction.CHALLENGE_3DS)

    def get_hash(self) -> str:
        """Get a stable hash of the rule content for change detection."""
        content = (
            f"{self.id}:{self.expr}:{self.action.value}:{self.score}:{self.state.value}"
        )
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]

    def to_dict(self) -> dict:
        """Convert rule to dictionary representation."""
        return {
            "id": self.id,
            "expr": self.expr,
            "action": self.action.value,
            "score": self.score,
            "state": self.state.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Rule":
        """Create rule from dictionary representation."""
        return cls(
            id=data["id"],
            expr=data.get(
                "if", data.get("expr", "")
            ),  # Support both 'if' and 'expr' keys
            action=RuleAction(data["action"]),
            score=data.get("score", 0.9),
            state=RuleState(data.get("state", "audit")),
        )


def validate_rule_id(rule_id: str) -> None:
    """
    Validate that a rule ID follows the required pattern.

    Args:
        rule_id: Rule identifier to validate

    Raises:
        ValueError: If rule ID is invalid
    """
    if not rule_id:
        raise ValueError("Rule ID cannot be empty")

    if not RULE_ID_PATTERN.match(rule_id):
        raise ValueError(
            f"Rule ID '{rule_id}' invalid. Must contain only lowercase letters, "
            f"numbers, and underscores. Pattern: {RULE_ID_PATTERN.pattern}"
        )


def validate_score(score: float) -> None:
    """
    Validate that a rule score is in the valid range.

    Args:
        score: Score value to validate

    Raises:
        ValueError: If score is out of range
    """
    if not isinstance(score, (int, float)):
        raise ValueError(f"Score must be a number, got: {type(score).__name__}")

    if not (0.0 <= score <= 1.0):
        raise ValueError(f"Score must be between 0.0 and 1.0, got: {score}")
