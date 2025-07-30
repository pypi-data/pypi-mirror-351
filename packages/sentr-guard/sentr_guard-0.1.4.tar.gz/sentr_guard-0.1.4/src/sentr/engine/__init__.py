"""
Engine module for fraud detection decision making.

Provides the main decision engine and verdict types.
"""

from .decision_engine import DecisionEngine
from .verdict import Verdict

__all__ = ["DecisionEngine", "Verdict"]
