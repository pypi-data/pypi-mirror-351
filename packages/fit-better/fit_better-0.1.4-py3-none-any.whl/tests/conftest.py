"""
Pytest configuration file.
Modifies the Python path to include the project's root directory.
Also configures warning filters for known third-party deprecation warnings.
"""

import sys
import os
import warnings
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Filter out known deprecation warnings from third-party libraries
warnings.filterwarnings(
    "ignore",
    message="The distutils package is deprecated and slated for removal in Python 3.12",
    category=DeprecationWarning,
)
