"""\nCentralized Logging Configuration for `fit_better`\n==================================================\n\nAuthor: xlindo\nCreate Time: 2025-05-10\n\nThis module provides a standardized way to configure and use logging across the\nentire `fit_better` package. It ensures consistent log formats, levels, and\noutput destinations (console and/or file) for all modules and potentially for\nparallel worker processes.\n\nKey Objectives:\n---------------\n\n*   **Consistency**: Apply a uniform logging setup (format, level, handlers) package-wide.\n*   **Simplicity**: Offer a simple `get_logger(__name__)` function for modules to obtain a logger instance.\n*   **Centralized Control**: Allow application-level configuration of logging (e.g., in a main script).\n*   **File Logging**: Optionally direct logs to a file for persistent storage.\n*   **Parallel Process Support**: Provide utilities (`setup_worker_logging`) to help configure logging\n    in child/worker processes (e.g., when using `joblib.Parallel`) based on settings from the main process.\n
Core Functions:\n---------------\n\n*   **`setup_logging(log_path=None, level=logging.INFO, format_str=...)`**: \n    This is the main configuration function. It should ideally be called once at the\n    beginning of the application's execution (e.g., in the main script or entry point).\n    *   Configures the root logger.\n    *   Removes any pre-existing handlers to avoid duplication.\n    *   Adds a console handler (StreamHandler) by default.\n    *   If `log_path` is provided, adds a file handler (FileHandler) to write logs to the specified file.\n    *   Sets the logging level and format for all handlers.\n    *   Sets a global flag `_LOGGING_CONFIGURED` to prevent re-configuration.\n    *   If `log_path` is used, it stores `LOG_PATH` and `LOG_LEVEL` as environment variables, which can be picked up by `setup_worker_logging` in child processes.\n
*   **`get_logger(name: str) -> logging.Logger`**:\n    The recommended way for any module in `fit_better` to obtain a logger instance.\n    It simply calls `logging.getLogger(name)`, ensuring that the logger inherits\n    the configuration set by `setup_logging`. Using `__name__` for the `name` argument\n    is a common Python practice, which makes log messages clearly attributable to their source module.\n
*   **`setup_worker_logging()`**:\n    Designed to be called at the start of a worker process (e.g., a function executed by `joblib.Parallel`).\n    It attempts to read `LOG_PATH` and `LOG_LEVEL` from environment variables (which should have been\n    set by `setup_logging` in the parent process if file logging was enabled).\n    If these variables are found, it calls `setup_logging` to configure logging for the worker, thereby\n    ensuring workers log to the same file and with the same level as the main process.\n
Usage Example:\n--------------
\n**In your main application script (e.g., `run_experiment.py`):**
```python
from fit_better.utils.logging_utils import setup_logging, get_logger
import logging

# Configure logging for the entire application at the beginning
# This will log INFO and above to console and to 'experiment.log'
setup_logging(log_path="experiment.log", level=logging.INFO)

# Get a logger for this main script
logger = get_logger(__name__)

logger.info("Application started.")
logger.debug("This debug message will not appear due to INFO level.")

# ... rest of your application ...
```

**In a module within `fit_better` (e.g., `fit_better/core/regression.py`):**
```python
from fit_better.utils.logging_utils import get_logger

# Get a logger specific to this module
logger = get_logger(__name__)

class RegressionFlow:
    def __init__(self):
        logger.info("RegressionFlow initialized.")

    def run_analysis(self):
        logger.debug("Starting analysis...") # Will only appear if level is DEBUG
        # ... analysis code ...
        logger.info("Analysis complete.")
```

**In a function that might be run in parallel by `joblib`:**
```python
from fit_better.utils.logging_utils import setup_worker_logging, get_logger

def parallel_task(item):
    # Ensure worker process logging is configured
    setup_worker_logging()
    logger = get_logger(__name__ + ".parallel_task") # More specific logger name

    logger.info(f"Processing item {item} in worker.")
    # ... task logic ...
    return item * 2

# In main script, when using joblib:
# from joblib import Parallel, delayed
# results = Parallel(n_jobs=2)(delayed(parallel_task)(i) for i in range(5))
```

This setup ensures that logging is manageable, consistent, and informative throughout the `fit_better` package.
"""

import os
import logging
from typing import Optional, Dict, Any, List, Union
import time

# Global flag to track if logging has been set up
_LOGGING_CONFIGURED = False


def setup_logging(
    log_path: Optional[str] = None,
    level: int = logging.INFO,
    format_str: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
) -> logging.Logger:
    """
    Configure logging for the entire application.

    This function should be called once at the start of the application to ensure
    consistent logging across all modules.

    Args:
        log_path: Path to the log file (if None, logs to console only)
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        format_str: Format string for the log messages

    Returns:
        Root logger configured with the specified settings
    """
    global _LOGGING_CONFIGURED

    # If already configured, just return the root logger
    if _LOGGING_CONFIGURED:
        return logging.getLogger()

    # Remove any existing handlers to avoid duplicate logging
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure the root logger
    root_logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(format_str)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if log_path is provided
    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Store log path and level in environment variables for worker processes
        os.environ["LOG_PATH"] = log_path
        os.environ["LOG_LEVEL"] = str(level)

    _LOGGING_CONFIGURED = True

    # Log the configuration
    root_logger.info(f"Logging initialized at level {logging.getLevelName(level)}")
    if log_path:
        root_logger.info(f"Log file: {log_path}")

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    This function ensures that all loggers in the application have consistent
    behavior. It should be used instead of logging.getLogger() directly.

    Args:
        name: Name of the logger, typically __name__ of the calling module

    Returns:
        Logger configured for the specified module
    """
    return logging.getLogger(name)


def setup_worker_logging():
    """
    Set up logging for worker processes.

    This function should be called at the start of each worker process to ensure
    consistent logging across all processes.
    """
    # Check if environment variables with logging config are set
    log_path = os.environ.get("LOG_PATH")
    log_level_str = os.environ.get("LOG_LEVEL")

    if log_path and log_level_str:
        try:
            log_level = int(log_level_str)
        except ValueError:
            # Try to use it as a level name if it's not a number
            log_level = getattr(logging, log_level_str.upper(), logging.INFO)

        # Configure logging for this worker
        setup_logging(log_path, log_level)

        # Get a logger for this function and log a message
        logger = get_logger(__name__)
        logger.debug("Worker process logging initialized")


# New functions for enhanced logging


class ProcessTracker:
    """
    Track the progress and timing of a process for logging purposes.

    Usage:
        with ProcessTracker(logger, "Training model") as tracker:
            # do training
            tracker.update("Completed first phase")
            # do more training
    """

    def __init__(self, logger, process_name: str):
        self.logger = logger
        self.process_name = process_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.process_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        if exc_type is not None:
            self.logger.error(
                f"Failed: {self.process_name} after {elapsed_time:.2f}s - {exc_val}"
            )
        else:
            self.logger.info(f"Completed: {self.process_name} in {elapsed_time:.2f}s")

    def update(self, message: str):
        """Log an update during process execution"""
        elapsed_time = time.time() - self.start_time
        self.logger.info(f"[{elapsed_time:.2f}s] {self.process_name}: {message}")


def log_model_results(
    logger, model_name: str, metrics: Dict[str, Any], use_ascii_table: bool = True
):
    """
    Log model evaluation results in a structured format.

    Args:
        logger: Logger instance
        model_name: Name of the model
        metrics: Dictionary of evaluation metrics
        use_ascii_table: Whether to use ASCII table formatting
    """
    from fit_better.utils.ascii import print_ascii_table

    if use_ascii_table:
        headers = ["Metric", "Value"]
        rows = [
            [k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in metrics.items()
        ]

        logger.info(f"\nResults for model: {model_name}")
        print_ascii_table(headers, rows, to_log=True)
    else:
        logger.info(f"Results for model: {model_name}")
        for k, v in metrics.items():
            if isinstance(v, float):
                logger.info(f"  {k}: {v:.6f}")
            else:
                logger.info(f"  {k}: {v}")


def log_summary(
    logger,
    results: Dict[str, Any],
    title: str = "Execution Summary",
    use_ascii_table: bool = True,
):
    """
    Log a summary of execution results.

    Args:
        logger: Logger instance
        results: Dictionary of result information
        title: Title for the summary section
        use_ascii_table: Whether to use ASCII table formatting
    """
    from fit_better.utils.ascii import print_ascii_table

    logger.info(f"\n{'-'*20} {title} {'-'*20}")

    if use_ascii_table:
        # Convert flat dict to rows
        headers = ["Key", "Value"]
        rows = [
            [k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in results.items()
        ]
        print_ascii_table(headers, rows, to_log=True)
    else:
        for k, v in results.items():
            if isinstance(v, float):
                logger.info(f"{k}: {v:.6f}")
            else:
                logger.info(f"{k}: {v}")

    logger.info(f"{'-'*20} End of {title} {'-'*20}\n")
