#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-16
Description: This script deliberately fails to test error handling.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for deliberately failing script."""
    logger.info("Starting deliberately failing test script")

    # This will raise an exception
    logger.info("About to fail...")
    raise RuntimeError("This test is designed to fail")

    # This should never be reached
    logger.info("This should never be logged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
