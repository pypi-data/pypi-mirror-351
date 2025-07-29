"""
Evaluation module for fit_better package

This module provides evaluation utilities for regression results,
including statistics, metrics, and reporting tools.
"""

# Import submodules to make them available through the evaluation namespace
from . import metrics

# Import commonly used functions
from .metrics import key_statistics

__all__ = ["metrics", "key_statistics"]
