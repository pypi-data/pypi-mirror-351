"""
Models module for fit_better package

This module contains various regression model implementations and utilities.
"""

# Import submodules to make them available through the models namespace
from . import sklearn

# Import commonly used classes and functions
from .sklearn import (
    AdaptivePartitionRegressor,
    PartitionTransformer,
    RegressorType,
    PartitionMode,
    evaluate_model,
)

__all__ = [
    "sklearn",
    "AdaptivePartitionRegressor",
    "PartitionTransformer",
    "RegressorType",
    "PartitionMode",
    "evaluate_model",
]
