"""
Utility functions for argument parsing in test scripts.

This module provides reusable argument parsing functions to reduce code duplication
across test scripts. It includes standard argument groups for:
- Input/output data files
- Partitioning and regression parameters
- Performance and parallelization options

Usage:
    from tests.utils.argparse_utils import add_io_args, add_model_args, add_output_args

    parser = argparse.ArgumentParser(description="My test script")
    add_io_args(parser)
    add_model_args(parser)
    add_output_args(parser)
    # Add any additional script-specific arguments
    args = parser.parse_args()
"""

import os
import argparse
from pathlib import Path
from fit_better import PartitionMode, RegressorType


def add_io_args(parser, default_data_dir=None):
    """
    Add common input/output file arguments to an argument parser.

    Args:
        parser: The argparse.ArgumentParser instance
        default_data_dir: Default directory for data files (if None, uses tests/data_gen/data)

    Returns:
        The group object for further customization if needed
    """
    if default_data_dir is None:
        tests_dir = Path(__file__).resolve().parent.parent
        default_data_dir = str(tests_dir / "data_gen" / "data")

    group = parser.add_argument_group("Input/Output Data")
    group.add_argument(
        "--input-dir",
        type=str,
        default=default_data_dir,
        help="Directory containing input data files",
    )
    group.add_argument(
        "--x-train", type=str, default="X_train.npy", help="Filename for X_train data"
    )
    group.add_argument(
        "--y-train", type=str, default="y_train.npy", help="Filename for y_train data"
    )
    group.add_argument(
        "--x-test", type=str, default="X_test.npy", help="Filename for X_test data"
    )
    group.add_argument(
        "--y-test", type=str, default="y_test.npy", help="Filename for y_test data"
    )
    group.add_argument(
        "--delimiter",
        type=str,
        default=None,
        help="Delimiter character for CSV or TXT files (default: ' ' for TXT, ',' for CSV)",
    )
    group.add_argument(
        "--header",
        type=str,
        choices=["infer", "none"],
        default="infer",
        help="Whether to use first row as headers in CSV/TXT files (default: infer)",
    )

    return group


def add_model_args(parser, include_partition=True, include_regressor=True):
    """
    Add common model parameter arguments to an argument parser.

    Args:
        parser: The argparse.ArgumentParser instance
        include_partition: Whether to include partition-related arguments
        include_regressor: Whether to include regressor-related arguments

    Returns:
        The group object for further customization if needed
    """
    group = parser.add_argument_group("Model Parameters")

    if include_partition:
        group.add_argument(
            "--partition-mode",
            type=str,
            default="KMEANS",
            choices=[mode.name for mode in PartitionMode],
            help="Partition mode to use",
        )
        group.add_argument(
            "--n-partitions", type=int, default=5, help="Number of partitions to create"
        )

    if include_regressor:
        group.add_argument(
            "--regressor-type",
            type=str,
            default="RANDOM_FOREST",
            choices=[regressor.name for regressor in RegressorType],
            help="Regressor type to use",
        )

    group.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")

    group.add_argument(
        "--use-regression-flow",
        action="store_true",
        help="Use RegressionFlow for a more streamlined workflow",
    )

    return group


def add_output_args(parser, default_output_dir=None):
    """
    Add common output arguments to an argument parser.

    Args:
        parser: The argparse.ArgumentParser instance
        default_output_dir: Default directory for output files (if None, uses tests/data_gen/model_results)

    Returns:
        The group object for further customization if needed
    """
    tests_dir = Path(__file__).resolve().parent.parent

    if default_output_dir is None:
        default_output_dir = str(tests_dir / "data_gen" / "model_results")
    else:
        # If a relative path is provided, place it under tests/data_gen
        if not os.path.isabs(default_output_dir):
            default_output_dir = str(tests_dir / "data_gen" / default_output_dir)
        # For absolute paths make sure they're under tests/data_gen
        elif not str(default_output_dir).startswith(str(tests_dir / "data_gen")):
            # Extract just the directory name
            dir_name = os.path.basename(default_output_dir)
            default_output_dir = str(tests_dir / "data_gen" / dir_name)

    group = parser.add_argument_group("Output Options")
    group.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help="Directory to save results",
    )
    group.add_argument(
        "--save-predictions",
        action="store_true",
        help="Save training and evaluation predictions to CSV files",
    )

    return group


def add_preprocessing_args(parser):
    """
    Add common preprocessing arguments to an argument parser.

    Args:
        parser: The argparse.ArgumentParser instance

    Returns:
        The group object for further customization if needed
    """
    group = parser.add_argument_group("Preprocessing Options")
    group.add_argument(
        "--impute-strategy",
        type=str,
        choices=["mean", "median", "most_frequent", "constant"],
        default="mean",
        help="Strategy for imputing missing values",
    )
    group.add_argument(
        "--impute-value",
        type=float,
        default=0,
        help="Value to use with 'constant' imputation strategy",
    )
    group.add_argument(
        "--drop-na",
        action="store_true",
        help="Drop rows with any NaN values instead of imputing",
    )

    return group


def add_logging_args(parser, default_log_dir=None):
    """
    Add common logging arguments to an argument parser.

    Args:
        parser: The argparse.ArgumentParser instance
        default_log_dir: Default directory for log files (if None, uses tests/data_gen/logs)

    Returns:
        The group object for further customization if needed
    """
    if default_log_dir is None:
        tests_dir = Path(__file__).resolve().parent.parent
        default_log_dir = str(tests_dir / "data_gen" / "logs")

    group = parser.add_argument_group("Logging Options")
    group.add_argument(
        "--log-dir",
        type=str,
        default=default_log_dir,
        help="Directory to save log files",
    )
    group.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level",
    )

    return group


def get_default_parser(description, **options):
    """
    Get a default argument parser with common argument groups.

    Args:
        description: Description for the parser
        **options: Options to control which argument groups to include
            io: Include input/output arguments (default: True)
            model: Include model arguments (default: True)
            output: Include output arguments (default: True)
            preprocessing: Include preprocessing arguments (default: True)
            logging: Include logging arguments (default: True)

    Returns:
        An argparse.ArgumentParser with common argument groups
    """
    parser = argparse.ArgumentParser(description=description)

    if options.get("io", True):
        add_io_args(parser)

    if options.get("model", True):
        add_model_args(parser)

    if options.get("output", True):
        add_output_args(parser)

    if options.get("preprocessing", True):
        add_preprocessing_args(parser)

    if options.get("logging", True):
        add_logging_args(parser)

    return parser
