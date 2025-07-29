"""
Author: xlindo
Create Time: 2025-05-10
Description: Utilities for exporting trained models to different formats for deployment
Usage:
    from fit_better.io.export.cpp import export_model_to_json
    export_model_to_json(model_result, "my_model.json")
"""

import os
import json
import warnings
import numpy as np
from fit_better.utils.logging_utils import get_logger

# Set up logging
logger = get_logger(__name__)

# Track available export formats
EXPORT_FORMATS = {"json": True}  # Only JSON format is supported


# ---------------------- JSON Export ----------------------
# Always available as it only uses standard libraries
def _get_input_feature_count(model_result):
    """
    Determine the number of input features required by the model
    """
    model = model_result["model"]

    # Check for explicit feature count in model_result
    if "input_feature_count" in model_result:
        return model_result["input_feature_count"]

    # Try to infer from model
    if hasattr(model, "n_features_in_"):
        return model.n_features_in_

    # For linear models
    if hasattr(model, "coef_"):
        if model.coef_.ndim == 1:
            return len(model.coef_)
        else:
            return model.coef_.shape[1]

    # For tree-based models
    if hasattr(model, "feature_importances_"):
        return len(model.feature_importances_)

    # Default fallback
    warnings.warn("Could not determine input feature count, using default of 1")
    return 1


def _convert_preprocessor(preprocessor):
    """
    Convert a scikit-learn preprocessor to its JSON representation
    """
    from sklearn.preprocessing import StandardScaler, MinMaxScaler

    if isinstance(preprocessor, StandardScaler):
        params = {
            "type": "StandardScaler",
            "mean": preprocessor.mean_.tolist(),
            "scale": (
                1.0 / preprocessor.scale_
            ).tolist(),  # Using scale_ directly to avoid division by zero
        }
        return params

    elif isinstance(preprocessor, MinMaxScaler):
        params = {
            "type": "MinMaxScaler",
            "min": preprocessor.min_.tolist(),
            "scale": preprocessor.scale_.tolist(),
        }
        return params

    else:
        # Unsupported preprocessor
        raise ValueError(
            f"Unsupported preprocessor type for JSON export: {type(preprocessor).__name__}"
        )


def _convert_transformer(transformer):
    """
    Convert a feature transformer to its JSON representation
    """
    # Currently support is limited
    raise NotImplementedError("Feature transformer export is not yet implemented")


def _export_tree(tree):
    """
    Export a decision tree to JSON-compatible format
    Warning: This is a simplified representation suitable for basic trees
    """
    # Extract tree structure
    tree_dict = {}

    # Get node count
    n_nodes = tree.tree_.node_count
    children_left = tree.tree_.children_left
    children_right = tree.tree_.children_right
    feature = tree.tree_.feature
    threshold = tree.tree_.threshold
    value = tree.tree_.value

    # Create nodes array
    nodes = []
    for i in range(n_nodes):
        node = {"id": i, "value": float(value[i][0][0])}

        # If not a leaf node
        if children_left[i] != children_right[i]:
            node["feature"] = int(feature[i])
            node["threshold"] = float(threshold[i])
            node["left"] = int(children_left[i])
            node["right"] = int(children_right[i])

        nodes.append(node)

    tree_dict["nodes"] = nodes
    return tree_dict


def _convert_model(model):
    """
    Convert a scikit-learn model to its JSON representation
    """
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

    model_type = type(model).__name__
    params = {"type": model_type}

    if (
        isinstance(model, LinearRegression)
        or isinstance(model, Ridge)
        or isinstance(model, Lasso)
        or isinstance(model, ElasticNet)
    ):
        # Handle linear models
        params["coefficients"] = model.coef_.tolist()
        params["intercept"] = float(model.intercept_)

        # Add regularization parameters for relevant models
        if isinstance(model, Ridge):
            params["alpha"] = float(model.alpha)
        elif isinstance(model, Lasso):
            params["alpha"] = float(model.alpha)
        elif isinstance(model, ElasticNet):
            params["alpha"] = float(model.alpha)
            params["l1_ratio"] = float(model.l1_ratio)

    elif isinstance(model, DecisionTreeRegressor):
        # Handle decision tree models (simplified representation)
        params["max_depth"] = model.max_depth
        params["min_samples_split"] = model.min_samples_split
        params["feature_count"] = model.n_features_in_
        params["tree"] = _export_tree(model)

    elif isinstance(model, RandomForestRegressor):
        # Handle random forest models (simplified representation)
        params["n_estimators"] = model.n_estimators
        params["max_depth"] = model.max_depth
        params["min_samples_split"] = model.min_samples_split
        params["feature_count"] = model.n_features_in_

        # Export each tree in the forest
        trees = []
        for tree in model.estimators_:
            trees.append(_export_tree(tree))
        params["trees"] = trees

    elif isinstance(model, GradientBoostingRegressor):
        # Handle gradient boosting models
        params["n_estimators"] = model.n_estimators
        params["learning_rate"] = float(model.learning_rate)
        params["max_depth"] = model.max_depth
        params["feature_count"] = model.n_features_in_
        params["init"] = float(model.init_.constant_)  # Initial prediction value

        # Export each tree in the ensemble
        estimators = []
        for stage in model.estimators_:
            # GBM stores trees in a 2D array, but we only need the first tree from each stage
            # since we're only supporting regression (not multi-output)
            tree = stage[0]
            estimators.append(_export_tree(tree))
        params["estimators"] = estimators

    else:
        # Unsupported model type
        raise ValueError(f"Unsupported model type for JSON export: {model_type}")

    return params


def export_model_to_json(model_result, output_path=None):
    """
    Export a scikit-learn model to JSON format.

    Args:
        model_result: The trained scikit-learn model or model result dictionary to export
        output_path: Path to save the exported model (string path)

    Returns:
        True if export was successful, False otherwise
    """
    try:
        # Prepare model result dict if bare model provided
        if hasattr(model_result, "predict"):
            model = {"model": model_result}
        else:
            model = model_result

        # Get the actual model
        if "model" not in model:
            raise ValueError("Model result must contain a 'model' key")

        # Convert model paths to absolute paths
        if output_path:
            output_path = os.path.abspath(output_path)

        # Get feature count
        feature_count = _get_input_feature_count(model)

        # Get model name
        model_name = model.get("model_name", type(model["model"]).__name__)

        # Create output JSON structure with root-level keys expected by C++ implementation
        output = {
            "type": "fit_better_export",
            "format": "json",
            "version": "1.0",
            "feature_count": feature_count,
            "model_type": model_name,
            "model_params": _convert_model(model["model"]),
        }

        # Add preprocessor if available
        if "scaler" in model and model["scaler"] is not None:
            try:
                preprocessor = _convert_preprocessor(model["scaler"])
                # Place preprocessor in the expected location for C++ implementation
                output["preprocessors"] = [preprocessor]
            except Exception as e:
                warnings.warn(f"Could not export preprocessor: {str(e)}")

        # Add transformer if available
        if "transformer" in model and model["transformer"] is not None:
            try:
                transformer = _convert_transformer(model["transformer"])
                # Add transformer to output when fully implemented
                # output["transformers"] = [transformer]
                warnings.warn("Transformer export is not fully implemented")
            except Exception as e:
                warnings.warn(f"Could not export transformer: {str(e)}")

        # Ensure directory exists if output_path provided
        if output_path:
            # Create directory if needed
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # Save the JSON to file
            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)

            logger.info(f"Model successfully exported to {output_path}")

        return True

    except Exception as e:
        logger.error(f"Error exporting model to JSON: {str(e)}")
        return False


# ---------------------- Export Format Registry ----------------------
def get_available_export_formats():
    """
    Return a list of available export formats.

    Returns:
        list: List of available export format names
    """
    # Only include JSON format
    return ["json"]


def export_model(model, X_sample=None, output_path=None, format="auto"):
    """
    Export a scikit-learn model to the specified format.

    Args:
        model: The trained scikit-learn model to export
        X_sample: Sample input data to determine feature count
        output_path: Path to save the exported model
        format: Export format to use (auto, json)

    Returns:
        bool: True if export was successful, False otherwise

    Raises:
        ValueError: If the requested format is not supported
    """
    # Check inputs
    if model is None:
        raise ValueError("Model cannot be None")

    if X_sample is not None and (
        not isinstance(X_sample, np.ndarray) or X_sample.size == 0
    ):
        raise ValueError("X_sample must be a non-empty numpy array")

    if output_path is None:
        raise ValueError("output_path must be specified")

    if os.path.isdir(output_path):
        raise ValueError(
            f"output_path must be a file path, not a directory: {output_path}"
        )

    # Determine format from file extension if set to auto
    export_format = format
    if export_format == "auto":
        _, ext = os.path.splitext(output_path)
        if ext.lower() == ".json":
            export_format = "json"
        else:
            raise ValueError(
                f"Could not determine export format from file extension: {ext}"
            )

    # Check if the requested format is available
    available_formats = get_available_export_formats()
    if export_format not in available_formats:
        raise ValueError(
            f"Unknown export format: {export_format}. Only 'json' is supported."
        )

    # Export to the requested format
    if export_format == "json":
        return export_model_to_json(model, output_path)
    else:
        raise ValueError(f"Export format '{export_format}' is not implemented")
