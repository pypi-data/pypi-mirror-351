"""
Verdict dataclass for decision engine output.

Represents the final fraud detection decision with score, reasons, and revision tracking.
"""

from dataclasses import dataclass
from typing import Literal, Tuple


@dataclass(slots=True, frozen=True)
class Verdict:
    """
    Immutable verdict from the fraud detection decision engine.

    Attributes:
        decision: Final action to take (allow/block/challenge_3ds)
        score: Highest rule score or ML score (0.0-1.0)
        reasons: Rule IDs or ML model names that contributed to decision
        revision: RuleSet revision hash for audit trail
    """

    decision: Literal["allow", "block", "challenge_3ds"]
    score: float
    reasons: Tuple[str, ...]
    revision: str

    def __post_init__(self):
        """Validate verdict fields after creation."""
        # Validate score range
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")

        # Validate decision value
        valid_decisions = {"allow", "block", "challenge_3ds"}
        if self.decision not in valid_decisions:
            raise ValueError(
                f"Decision must be one of {valid_decisions}, got {self.decision}"
            )

        # Ensure reasons is a tuple
        if not isinstance(self.reasons, tuple):
            raise ValueError(f"Reasons must be a tuple, got {type(self.reasons)}")

    @property
    def is_blocking(self) -> bool:
        """Check if this verdict blocks the transaction."""
        return self.decision == "block"

    @property
    def is_challenging(self) -> bool:
        """Check if this verdict requires 3DS challenge."""
        return self.decision == "challenge_3ds"

    @property
    def is_allowing(self) -> bool:
        """Check if this verdict allows the transaction."""
        return self.decision == "allow"

    def to_dict(self) -> dict:
        """Convert verdict to dictionary for JSON serialization."""
        return {
            "decision": self.decision,
            "score": self.score,
            "reasons": list(self.reasons),
            "revision": self.revision,
        }
