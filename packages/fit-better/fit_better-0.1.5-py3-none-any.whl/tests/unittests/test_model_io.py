"""
Unit tests for model I/O functionality.

This test suite validates:
- Model saving and loading
- Model serialization
- Backwards compatibility
- Error handling
"""

import os
import sys
import pytest
import numpy as np
import pickle
import tempfile
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from fit_better.io.model_io import (
    save_model,
    load_model,
    serialize_model,
    deserialize_model,
)


@pytest.fixture
def trained_linear_model():
    """Create a simple trained linear model for testing."""
    np.random.seed(42)
    X = np.random.rand(100, 1)
    y = 2 * X.flatten() + 3 + np.random.normal(0, 0.5, 100)

    model = LinearRegression()
    model.fit(X, y)
    return model, X, y


@pytest.fixture
def trained_complex_model():
    """Create a more complex trained model for testing."""
    np.random.seed(42)
    X = np.random.rand(100, 3)  # 3 features
    y = 2 * X[:, 0] + 3 * X[:, 1] - X[:, 2] + np.random.normal(0, 0.3, 100)

    model = RandomForestRegressor(n_estimators=10, max_depth=3, random_state=42)
    model.fit(X, y)
    return model, X, y


@pytest.mark.unit
class TestModelIO:
    """Test suite for model I/O functionality."""

    def test_save_and_load_linear_model(self, trained_linear_model, tmp_path):
        """Test saving and loading a linear model."""
        model, X, y = trained_linear_model

        # Define output path
        model_path = os.path.join(tmp_path, "linear_model.pkl")

        # Save the model
        success = save_model(model, model_path)

        # Check that saving was successful
        assert success, "Model saving should return True on success"
        assert os.path.exists(model_path), "Model file should exist"
        assert os.path.getsize(model_path) > 0, "Model file should not be empty"

        # Load the model
        loaded_model_dict = load_model(model_path)

        # Check that the model was loaded successfully
        assert loaded_model_dict is not None, "Loaded model dict should not be None"
        assert isinstance(
            loaded_model_dict, dict
        ), "Loaded model should be a dictionary"
        assert "model" in loaded_model_dict, "Loaded dict should contain 'model' key"

        # Extract the actual model from the dictionary
        loaded_model = loaded_model_dict["model"]
        assert isinstance(
            loaded_model, LinearRegression
        ), "Loaded model should be a LinearRegression"

        # Check that the loaded model has the same coefficients
        assert np.allclose(model.coef_, loaded_model.coef_), "Coefficients should match"
        assert np.allclose(
            model.intercept_, loaded_model.intercept_
        ), "Intercept should match"

        # Check that the loaded model makes the same predictions
        original_preds = model.predict(X)
        loaded_preds = loaded_model.predict(X)
        assert np.allclose(original_preds, loaded_preds), "Predictions should match"

    def test_save_and_load_complex_model(self, trained_complex_model, tmp_path):
        """Test saving and loading a more complex model."""
        model, X, y = trained_complex_model

        # Define output path
        model_path = os.path.join(tmp_path, "complex_model.pkl")

        # Save the model
        success = save_model(model, model_path)

        # Check that saving was successful
        assert success, "Model saving should return True on success"
        assert os.path.exists(model_path), "Model file should exist"

        # Load the model
        loaded_model_dict = load_model(model_path)

        # Check that the model was loaded successfully
        assert loaded_model_dict is not None, "Loaded model dict should not be None"
        assert isinstance(
            loaded_model_dict, dict
        ), "Loaded model should be a dictionary"
        assert "model" in loaded_model_dict, "Loaded dict should contain 'model' key"

        # Extract the actual model from the dictionary
        loaded_model = loaded_model_dict["model"]
        assert isinstance(
            loaded_model, RandomForestRegressor
        ), "Loaded model should be a RandomForestRegressor"

        # Check that the loaded model makes the same predictions
        original_preds = model.predict(X)
        loaded_preds = loaded_model.predict(X)
        assert np.allclose(original_preds, loaded_preds), "Predictions should match"

    def test_serialize_and_deserialize(self, trained_linear_model):
        """Test model serialization and deserialization."""
        model, X, y = trained_linear_model

        # Serialize the model
        serialized = serialize_model(model)

        # Check that serialization succeeded
        assert serialized is not None, "Serialized model should not be None"
        assert isinstance(serialized, bytes), "Serialized model should be bytes"
        assert len(serialized) > 0, "Serialized model should not be empty"

        # Deserialize the model
        deserialized = deserialize_model(serialized)

        # Check that deserialization succeeded
        assert deserialized is not None, "Deserialized model should not be None"
        assert isinstance(
            deserialized, LinearRegression
        ), "Deserialized model should be a LinearRegression"

        # Check that the deserialized model has the same coefficients
        assert np.allclose(model.coef_, deserialized.coef_), "Coefficients should match"
        assert np.allclose(
            model.intercept_, deserialized.intercept_
        ), "Intercept should match"

        # Check that the deserialized model makes the same predictions
        original_preds = model.predict(X)
        deserialized_preds = deserialized.predict(X)
        assert np.allclose(
            original_preds, deserialized_preds
        ), "Predictions should match"

    def test_error_handling(self, trained_linear_model, tmp_path):
        """Test error handling during model I/O operations."""
        model, X, y = trained_linear_model

        # Test loading non-existent file
        nonexistent_path = os.path.join(tmp_path, "nonexistent.pkl")
        with pytest.raises(FileNotFoundError):
            load_model(nonexistent_path)

        # Create a directory where a file should be, making it impossible to save there
        file_as_dir_path = os.path.join(tmp_path, "file_as_dir.pkl")
        os.makedirs(file_as_dir_path, exist_ok=True)

        # Attempt to save to a directory instead of a file
        try:
            save_model(model, file_as_dir_path, overwrite=True)
            assert False, "Saving to a directory should fail but didn't"
        except Exception:
            # We expect this to fail, so this is a success
            pass

        # Test deserializing invalid data
        with pytest.raises((pickle.UnpicklingError, EOFError, AttributeError)):
            deserialize_model(b"invalid data")

    def test_save_with_metadata(self, trained_linear_model, tmp_path):
        """Test saving model with metadata."""
        model, X, y = trained_linear_model

        # Define output path
        model_path = os.path.join(tmp_path, "model_with_metadata.pkl")

        # Create metadata
        metadata = {
            "name": "test_model",
            "version": "1.0",
            "features": ["feature1"],
            "target": "target",
            "created_at": "2025-01-01",
        }

        # Save the model with metadata
        success = save_model(model, model_path, metadata=metadata)

        # Check that saving was successful
        assert success, "Model saving should return True on success"

        # Load the model
        loaded_model, loaded_metadata = load_model(model_path, return_metadata=True)

        # Check that the model and metadata were loaded successfully
        assert loaded_model is not None, "Loaded model should not be None"
        assert loaded_metadata is not None, "Loaded metadata should not be None"
        assert isinstance(
            loaded_metadata, dict
        ), "Loaded metadata should be a dictionary"

        # Check metadata contents
        assert loaded_metadata["name"] == "test_model", "Name metadata should match"
        assert loaded_metadata["version"] == "1.0", "Version metadata should match"
        assert loaded_metadata["features"] == [
            "feature1"
        ], "Features metadata should match"
        assert loaded_metadata["target"] == "target", "Target metadata should match"
        assert (
            loaded_metadata["created_at"] == "2025-01-01"
        ), "Creation date metadata should match"
