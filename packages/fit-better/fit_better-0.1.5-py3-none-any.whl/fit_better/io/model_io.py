"""
Author: xlindo
Create Time: 2025-05-10
Description: Model I/O utilities for saving, loading, and prediction.

This module provides functions for saving and loading regression models,
with support for optional preprocessing transformers. It handles both single
models and complex model dictionaries with metadata.

Usage:
    # Save a model
    from fit_better.io import save_model
    save_model(trained_model, "model.joblib", transformer=preprocessor)

    # Load a model
    from fit_better.io import load_model
    model_dict = load_model("model.joblib")

    # Predict with a model
    from fit_better.io import predict_with_model
    predictions = predict_with_model("model.joblib", X_test)
"""

import os
import logging
import pickle
import joblib
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
from sklearn.base import BaseEstimator

logger = logging.getLogger(__name__)


def save_model(
    model: Union[BaseEstimator, Dict[str, Any]],
    filepath: str,
    transformer: Optional[BaseEstimator] = None,
    overwrite: bool = False,
    compress: int = 3,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Save a model with optional transformer to a file.

    Args:
        model: The trained model or model result dictionary
        filepath: Path to save the model
        transformer: Optional preprocessing transformer
        overwrite: Whether to overwrite existing files
        compress: Compression level (0-9)
        metadata: Optional metadata dictionary

    Returns:
        Path to the saved model file if successful

    Raises:
        FileExistsError: If the file exists and overwrite is False
    """
    # Ensure directory exists
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        # Check if file exists
        if os.path.exists(filepath) and not overwrite:
            error_msg = (
                f"File {filepath} already exists. Set overwrite=True to replace it."
            )
            logger.error(f"Error saving model to {filepath}: {error_msg}")
            raise FileExistsError(error_msg)

        # Determine what to save
        if isinstance(model, dict) and "model" in model:
            # This is a model result dictionary
            if transformer is not None:
                logger.warning(
                    "Both transformer argument and model dict transformer found. "
                    "Using the provided transformer argument."
                )
            else:
                transformer = model.get("transformer")

            # Collect all metadata
            combined_metadata = {}
            # First add metadata from the model dict (excluding special keys)
            for key, value in model.items():
                if key not in ["model", "transformer", "scaler", "metadata"]:
                    combined_metadata[key] = value

            # Then add the explicit metadata dict, which takes precedence
            if "metadata" in model:
                combined_metadata.update(model["metadata"])
            if metadata:
                combined_metadata.update(metadata)

            save_dict = {
                "model": model["model"],
                "transformer": transformer,
                "scaler": model.get("scaler"),
                "metadata": combined_metadata,
            }
        else:
            # This is a bare model
            save_dict = {
                "model": model,
                "transformer": transformer,
                "scaler": None,
                "metadata": metadata or {},
            }

        # Save the model
        joblib.dump(save_dict, filepath, compress=compress)
        logger.info(f"Model saved successfully to {filepath}")
        return filepath
    except FileExistsError:
        # Re-raise the FileExistsError for proper handling
        raise
    except Exception as e:
        logger.error(f"Error saving model to {filepath}: {str(e)}")
        return None


def load_model(
    filepath: str, return_metadata: bool = False
) -> Union[Dict[str, Any], Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Load a model from a file.

    Args:
        filepath: Path to the saved model file
        return_metadata: Whether to return metadata along with model

    Returns:
        If return_metadata is False: Dictionary containing model and metadata
        If return_metadata is True: Tuple of (model_dict, metadata)

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file {filepath} not found")

    try:
        # Try loading with joblib (preferred)
        loaded = joblib.load(filepath)
        logger.info(f"Model loaded successfully from {filepath}")
    except Exception as joblib_error:
        try:
            # Fall back to pickle if joblib fails
            logger.warning(
                f"Joblib loading failed ({str(joblib_error)}). Trying pickle..."
            )
            with open(filepath, "rb") as f:
                loaded = pickle.load(f)
            logger.info(f"Model loaded successfully with pickle from {filepath}")
        except Exception as pickle_error:
            logger.error(
                f"Failed to load model from {filepath}. "
                f"Joblib error: {str(joblib_error)}. "
                f"Pickle error: {str(pickle_error)}"
            )
            raise

    # Handle different saved formats
    if isinstance(loaded, dict) and "model" in loaded:
        # This is our standard format
        model_dict = loaded
    else:
        # This is a bare model - convert to our standard format
        logger.warning(
            f"Model in {filepath} is not in standard format. "
            f"Converting to standard format."
        )
        model_dict = {
            "model": loaded,
            "transformer": None,
            "scaler": None,
            "metadata": {},
        }

    if return_metadata:
        return model_dict, model_dict.get("metadata", {})
    else:
        return model_dict


def predict_with_model(
    model_or_path: Union[str, Dict[str, Any], BaseEstimator],
    X: np.ndarray,
) -> np.ndarray:
    """
    Make predictions using a saved or loaded model.

    Args:
        model_or_path: Path to model file, loaded model dict, or bare model
        X: Input features

    Returns:
        Array of predictions

    Raises:
        ValueError: If the model format is invalid
    """
    # Load the model if a path is provided
    if isinstance(model_or_path, str):
        model_dict = load_model(model_or_path)
    else:
        model_dict = model_or_path

    # Extract model and transformers
    if isinstance(model_dict, dict) and "model" in model_dict:
        # This is our standard format
        model = model_dict["model"]
        transformer = model_dict.get("transformer")
        scaler = model_dict.get("scaler")
    elif hasattr(model_dict, "predict"):
        # This is a bare model
        model = model_dict
        transformer = None
        scaler = None
    else:
        raise ValueError(
            "Invalid model format. Expected a model path, result dictionary, "
            "or scikit-learn compatible model."
        )

    # Ensure X is in the right shape
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    # Apply preprocessing
    X_processed = X

    if transformer is not None:
        X_processed = transformer.transform(X_processed)

    if scaler is not None:
        X_processed = scaler.transform(X_processed)

    # Make predictions
    try:
        predictions = model.predict(X_processed)
        return predictions
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        raise


def serialize_model(model):
    """
    Serialize a model to bytes.

    Args:
        model: The model to serialize

    Returns:
        Serialized model as bytes
    """
    return pickle.dumps(model)


def deserialize_model(data):
    """
    Deserialize bytes to a model.

    Args:
        data: Serialized model as bytes

    Returns:
        Deserialized model
    """
    return pickle.loads(data)
