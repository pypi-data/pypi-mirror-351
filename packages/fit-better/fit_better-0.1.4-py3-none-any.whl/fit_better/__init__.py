"""
fit-better: An improved machine learning regression library

This package provides improved implementations of common regression algorithms,
with a focus on ease of use, performance, and extensibility.

The package includes:
- Linear models: Linear Regression, Ridge, Lasso, Elastic Net
- Tree-based models: Decision Trees, Random Forest, Gradient Boosting
- Model evaluation and selection tools
- Feature engineering utilities
- High-performance C++ deployment capabilities

The C++ implementation documentation is available in the utils.cpp_docs module.
"""

# Define version
__version__ = "0.1.0"

# Direct imports - these should be available at the top level
from .io.model_io import save_model, load_model, predict_with_model
from .data.file_loader import (
    load_data_from_files,
    load_dataset,
    preprocess_data_for_regression,
)
from .data.synthetic import (
    generate_synthetic_data,
    generate_synthetic_data_by_function,
    generate_train_test_data,
    save_data,
)
from .data.csv_manager import CSVMgr
from .utils.logging_utils import setup_logging
from .utils.statistics import (
    calc_regression_statistics,
    print_partition_statistics,
    calculate_total_performance,
    get_error_percentiles,
    format_statistics_table,
    compare_model_statistics,
)
from .utils.plotting import (
    plot_versus,
    plot_predictions_vs_actual,
    plot_error_distribution,
    create_regression_report_plots,
    plot_performance_comparison,
)

# Import core components
from .core.models import (
    RegressorType,
    create_regressor,
    fit_one_model,
    select_best_model,
    fit_all_regressors,
)
from .core.partitioning import (
    PartitionMode,
    train_models_on_partitions,
    predict_with_partitioned_models,
    get_partitioner_by_mode,
    get_partition_boundaries,
    get_partition_masks,
    partition_data,
    create_partition_boundaries,
    get_partition_boundary_names,
    transform_data_with_partitions,
    find_best_partition,
    compare_partitioning_methods,
)
from .core.regression import RegressionFlow, RegressionResult, Metric, DataDimension

# Import optional modules
# These imports are wrapped in try-except to allow the package to work
# even if some submodules are not available
try:
    from . import linear
except ImportError:
    # Module might not be available
    pass

try:
    from . import trees
except ImportError:
    # Module might not be available
    pass

try:
    from . import evaluation
except ImportError:
    # Module might not be available
    pass

try:
    from . import preprocessing
except ImportError:
    # Module might not be available
    pass

try:
    from . import io
except ImportError:
    # Module might not be available
    pass

# Add new clustering algorithms
from .models.sklearn import (
    DBSCANPartitionTransformer,
    OPTICSPartitionTransformer,
)
