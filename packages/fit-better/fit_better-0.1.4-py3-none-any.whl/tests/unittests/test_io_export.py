"""
Unit tests for model export functionality.

This test suite validates:
- Model export to JSON format
- Model export utilities and helpers
- Export format validation
"""

import os
import sys
import pytest
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import json
import tempfile

from fit_better.io.export.cpp import (
    export_model_to_json,
    export_model,
    get_available_export_formats,
)


@pytest.fixture
def trained_linear_model():
    """Create a simple trained linear model for export testing."""
    np.random.seed(42)
    X = np.random.rand(100, 1)
    y = 2 * X.flatten() + 3 + np.random.normal(0, 0.5, 100)

    model = LinearRegression()
    model.fit(X, y)
    return model, X, y


@pytest.fixture
def trained_rf_model():
    """Create a simple trained random forest model for export testing."""
    np.random.seed(42)
    X = np.random.rand(100, 2)  # 2 features
    y = 2 * X[:, 0] + 3 * X[:, 1] + np.random.normal(0, 0.5, 100)

    model = RandomForestRegressor(n_estimators=10, max_depth=3, random_state=42)
    model.fit(X, y)
    return model, X, y


@pytest.mark.unit
class TestModelExport:
    """Test suite for model export functionality."""

    def test_get_available_export_formats(self):
        """Test that available export formats are returned correctly."""
        formats = get_available_export_formats()

        # Check that formats is a list or tuple
        assert isinstance(
            formats, (list, tuple)
        ), "Export formats should be a list or tuple"

        # Check that json format is available
        assert "json" in formats, "JSON should be an available export format"

    def test_export_model_to_json(self, trained_linear_model, tmp_path):
        """Test exporting a model to JSON format."""
        model, X, y = trained_linear_model

        # Define output file path
        output_path = os.path.join(tmp_path, "model.json")

        # Create model_result dict for export
        model_result = {"model": model, "model_name": "LinearRegression"}

        # Export model to JSON
        result = export_model_to_json(model_result, output_path)

        # Check that export was successful
        assert result, "Export to JSON should return True on success"

        # Check that output file exists
        assert os.path.exists(output_path), "Output JSON file should exist"

        # Check that output file is not empty
        assert os.path.getsize(output_path) > 0, "Output JSON file should not be empty"

        # Check that output file is valid JSON
        with open(output_path, "r") as f:
            try:
                json_data = json.load(f)
                assert isinstance(
                    json_data, dict
                ), "Exported JSON should be a dictionary"
            except json.JSONDecodeError:
                pytest.fail("Exported JSON is not valid JSON")

    def test_export_model_format_selection(self, trained_linear_model, tmp_path):
        """Test that export_model correctly handles format selection."""
        model, X, y = trained_linear_model

        # Define output path for JSON format
        json_path = os.path.join(tmp_path, "model.json")

        # Prepare model for export
        model_result = {"model": model, "model_name": "LinearRegression"}

        # Export model to JSON format
        result_json = export_model(model_result, output_path=json_path, format="json")

        # Check that export was successful
        assert result_json, "Export to JSON should return True on success"

        # Check that output file exists
        assert os.path.exists(json_path), "Output JSON file should exist"

    def test_export_model_auto_format(self, trained_linear_model, tmp_path):
        """Test that export_model correctly infers format from file extension."""
        model, X, y = trained_linear_model

        # Define output path with json extension
        json_path = os.path.join(tmp_path, "model.json")

        # Prepare model for export
        model_result = {"model": model, "model_name": "LinearRegression"}

        # Export model without specifying format
        result_json = export_model(model_result, output_path=json_path)

        # Check that export was successful
        assert result_json, "Export to JSON should return True on success"

        # Check that output file exists
        assert os.path.exists(json_path), "Output JSON file should exist"

    def test_export_complex_model(self, trained_rf_model, tmp_path):
        """Test exporting a more complex model like Random Forest."""
        model, X, y = trained_rf_model

        # Define output file path
        json_path = os.path.join(tmp_path, "rf_model.json")

        # Prepare model for export
        model_result = {"model": model, "model_name": "RandomForestRegressor"}

        # Export model to JSON format
        result_json = export_model(model_result, output_path=json_path, format="json")

        # Check that export was successful
        assert result_json, "Export to JSON should return True on success"

        # Check that output file exists
        assert os.path.exists(json_path), "Output JSON file should exist"

    def test_export_input_validation(self, trained_linear_model, tmp_path):
        """Test that export functions validate input correctly."""
        model, X, y = trained_linear_model

        # Prepare model for export
        model_result = {"model": model, "model_name": "LinearRegression"}

        # Test with invalid format
        with pytest.raises(ValueError):
            export_model(
                model_result,
                output_path=os.path.join(tmp_path, "model.txt"),
                format="invalid_format",
            )

        # Test with directory instead of file path
        with pytest.raises(ValueError):
            export_model(model_result, output_path=tmp_path, format="json")

        # Test with None model
        with pytest.raises(ValueError):
            export_model(None, output_path=os.path.join(tmp_path, "model.json"))

        # Test with no output path
        with pytest.raises(ValueError):
            export_model(model_result, output_path=None)
