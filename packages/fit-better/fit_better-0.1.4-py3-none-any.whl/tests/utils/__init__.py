"""
Common utility functions for test scripts.

This package provides reusable functions to reduce code duplication across test scripts.
It includes modules for:
- argument parsing (argparse_utils)
- data loading and generation (data_utils)
- model evaluation (eval_utils, model_evaluation)
- visualization (viz_utils)

These utilities help maintain consistency across test scripts and reduce redundancy.
"""

# Import main functions from utility modules for easier access
from .argparse_utils import (
    get_default_parser,
    add_io_args,
    add_model_args,
    add_output_args,
    add_preprocessing_args,
    add_logging_args,
)

from .data_utils import (
    load_test_data,
    generate_synthetic_data,
    save_data_multiple_formats,
)

from .eval_utils import (
    evaluate_model,
    print_evaluation_report,
    evaluate_multiple_configurations,
)

# Import directly from fit_better.utils.plotting instead of deprecated viz_utils
from fit_better.utils.plotting import (
    create_regression_report_plots,
    visualize_results_comparison,
)

# For backward compatibility (deprecated)
from .viz_utils import create_performance_plots

# Import new unified model evaluation functionality
from .model_evaluation import (
    train_and_evaluate_model,
    find_best_model,
    save_predictions_to_csv,
    generate_comparison_visualizations,
)

import os
import logging
import time
from datetime import datetime


def setup_test_logging(test_name=None, log_dir="test_logs", log_level=logging.INFO):
    """
    Set up standardized logging for tests.

    Args:
        test_name: Name of the test (defaults to calling module name)
        log_dir: Directory to store log files
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    # If test_name not provided, try to get it from the calling module
    if test_name is None:
        import inspect

        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        test_name = module.__name__.split(".")[-1] if module else "unknown_test"

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{test_name}_{timestamp}.log")

    # Import the centralized logging utility
    try:
        from fit_better.utils.logging_utils import setup_logging, get_logger

        # Configure logging using the centralized utility
        setup_logging(log_path=log_file, level=log_level)
        logger = get_logger(test_name)
    except ImportError:
        # Fallback to basic logging configuration
        logging.basicConfig(
            filename=log_file,
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger(test_name)

        # Add console handler
        console = logging.StreamHandler()
        console.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console.setFormatter(formatter)
        logger.addHandler(console)

    logger.info(
        f"Test '{test_name}' started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return logger


def log_test_results(logger, test_results, use_ascii_table=True):
    """
    Log test results with a standardized format.

    Args:
        logger: Logger instance
        test_results: Dictionary of test results
        use_ascii_table: Whether to use ASCII table formatting
    """
    try:
        from fit_better.utils.logging_utils import log_summary

        log_summary(
            logger, test_results, title="Test Results", use_ascii_table=use_ascii_table
        )
    except ImportError:
        try:
            from fit_better.utils.ascii import print_ascii_table

            # Log using ASCII table
            if use_ascii_table:
                headers = ["Metric", "Value"]
                rows = [[k, str(v)] for k, v in test_results.items()]
                logger.info("\nTest Results:")
                print_ascii_table(headers, rows, to_log=True)
            else:
                logger.info("\n" + "-" * 20 + " Test Results " + "-" * 20)
                for k, v in test_results.items():
                    logger.info(f"{k}: {v}")
                logger.info("-" * 50)
        except ImportError:
            # Simple fallback if ASCII table is not available
            logger.info("\n" + "-" * 20 + " Test Results " + "-" * 20)
            for k, v in test_results.items():
                logger.info(f"{k}: {v}")
            logger.info("-" * 50)
