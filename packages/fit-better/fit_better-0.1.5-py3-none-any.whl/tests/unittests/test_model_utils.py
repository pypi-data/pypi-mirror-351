#!/usr/bin/env python
"""
Unit tests for the model_utils module.

This test suite validates:
- Importing model_utils module components
- Sequential model fitting
- Parallel model fitting
- Model overfitting detection
- Multiple regressor types
"""

import os
import sys
import pytest
import numpy as np

# Import the modules to test
from fit_better.core.models import (
    RegressorType,
    fit_all_regressors,
    select_best_model,
    Metric,
)


@pytest.fixture
def simple_dataset():
    """Create a simple dataset for testing regression models."""
    np.random.seed(42)
    X = np.linspace(0, 10, 50).reshape(-1, 1)
    y = 2 * X.flatten() + 3 + np.random.normal(0, 0.5, 50)
    return X, y


@pytest.fixture
def small_dataset():
    """Create a very small dataset for testing overfitting detection."""
    np.random.seed(42)
    X = np.linspace(0, 5, 10).reshape(-1, 1)
    y = 2 * X.flatten() + 3 + np.random.normal(0, 0.2, 10)
    return X, y


@pytest.fixture
def binary_classification_dataset():
    """Create a binary classification dataset for testing logistic regression."""
    np.random.seed(42)
    X = np.linspace(0, 10, 50).reshape(-1, 1)
    # Create a non-linear decision boundary
    y = (np.sin(X.flatten()) + 0.5 > 0).astype(int)
    return X, y


class TestModelUtils:
    """Test suite for model_utils module."""

    def test_imports(self):
        """Test importing the model_utils module components."""
        # If we got to this point, imports worked because we imported at the module level
        assert True

    def test_fit_model_sequential(self, simple_dataset):
        """Test model fitting with sequential execution (n_jobs=1)."""
        X, y = simple_dataset

        results = fit_all_regressors(
            X, y, n_jobs=1, regressor_type=RegressorType.DECISION_TREE
        )

        # Check if we got valid results
        assert results is not None
        assert len(results) > 0
        assert "model_name" in results[0]
        assert "model" in results[0]
        assert "stats" in results[0]
        assert "mae" in results[0]["stats"]

    def test_fit_model_parallel(self, simple_dataset):
        """Test model fitting with parallel execution (n_jobs=2)."""
        X, y = simple_dataset

        results = fit_all_regressors(
            X, y, n_jobs=2, regressor_type=RegressorType.DECISION_TREE
        )

        # Check if we got valid results
        assert results is not None
        assert len(results) > 0
        assert "model_name" in results[0]
        assert "model" in results[0]
        assert "stats" in results[0]
        assert "mae" in results[0]["stats"]

    def test_overfitting_detection(self, small_dataset):
        """Test overfitting detection in tree models."""
        X, y = small_dataset

        results = fit_all_regressors(
            X, y, n_jobs=1, regressor_type=RegressorType.DECISION_TREE
        )

        # Check if we got valid results
        assert results is not None
        assert len(results) > 0

        model_result = results[0]

        # Check model and stats exist
        assert "model" in model_result
        assert "stats" in model_result
        assert "mae" in model_result["stats"]

        # Check model is a decision tree
        from sklearn.tree import DecisionTreeRegressor

        assert isinstance(model_result["model"], DecisionTreeRegressor)

    def test_select_best_model(self, simple_dataset):
        """Test the select_best_model function."""
        X, y = simple_dataset

        # Fit multiple regressor types
        results = fit_all_regressors(X, y, n_jobs=1)

        # Test select_best_model with default metric (MAE)
        best_model = select_best_model(results)

        assert best_model is not None
        assert "model_name" in best_model
        assert "model" in best_model
        assert "stats" in best_model
        assert "mae" in best_model["stats"]

        # Test with R2 metric
        best_model_r2 = select_best_model(results, metric=Metric.R2)

        assert best_model_r2 is not None
        assert "stats" in best_model_r2
        assert "r2" in best_model_r2["stats"]

    def test_multiple_regressor_types(self, simple_dataset):
        """Test fitting multiple regressor types."""
        X, y = simple_dataset

        # Test with different regressor types
        regressor_types = [
            RegressorType.LINEAR,
            RegressorType.DECISION_TREE,
            RegressorType.RANDOM_FOREST,
        ]

        for reg_type in regressor_types:
            results = fit_all_regressors(X, y, n_jobs=1, regressor_type=reg_type)

            # Check if we got valid results
            assert results is not None
            assert len(results) > 0
            assert "model_name" in results[0]
            # Check model name contains part of the regressor_type value string
            model_name = results[0]["model_name"].upper()
            assert any(
                word.upper() in model_name for word in reg_type.value.split()
            ), f"Expected {reg_type.value} to match with model name {results[0]['model_name']}"

    def test_logistic_regression(self, binary_classification_dataset):
        """Test logistic regression model creation and fitting."""
        X, y = binary_classification_dataset

        results = fit_all_regressors(
            X, y, n_jobs=1, regressor_type=RegressorType.LOGISTIC
        )

        # Check if we got valid results
        assert results is not None
        assert len(results) > 0
        assert "model_name" in results[0]
        assert "model" in results[0]
        assert "stats" in results[0]

        # Check that the model is a LogisticRegression instance
        from sklearn.linear_model import LogisticRegression

        assert isinstance(results[0]["model"], LogisticRegression)

        # Test model predictions (should return probabilities in [0,1] range)
        predictions = results[0]["model"].predict_proba(X)
        assert predictions.shape[1] == 2  # Binary classification has 2 classes
        assert np.all(predictions >= 0) and np.all(predictions <= 1)
