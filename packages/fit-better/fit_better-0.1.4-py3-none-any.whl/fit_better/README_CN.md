# Fit Better 核心模块

**作者：** hi@xlindo.com  
**更新日期：** 2025-05-10

本工具包提供全面的 Python 和 C++ 工具，用于智能回归建模、数据生成、评估、模型管理和部署。通过模块化组件覆盖回归工作流的每个阶段，支持灵活实验和可靠日志记录。同时支持 Python 与 C++ 部署，并通过跨语言测试确保一致性。

## 核心组件

- **model_utils.py**：模型训练、选择与评估工具
- **partition_utils.py**：数据分区策略实现
- **sklearn_utils.py**：增强的 scikit-learn 集成，支持变换器与元估计器
- **plot_utils.py**：可视化工具
- **stats_utils.py**：统计分析工具
- **data_utils.py**：数据加载与预处理工具
- **io.py**：模型序列化、导出和导入操作
- **cpp_export.py**：C++ 部署和代码生成管理

## 主要 API

本包提供简化的 API 便于使用：

```python
from fit_better import RegressionFlow, PartitionMode, RegressorType, Metric
```

## 模块详情

### model_utils.py

- 回归器类型和评估指标的枚举
- 拟合各种回归模型的函数
- 基于性能指标的模型选择
- 超参数优化工具

### partition_utils.py

- 实现不同的数据分区策略
- 在分区数据上训练模型的函数
- 边界确定和验证
- 分区可视化和分析

### sklearn_utils.py

- 兼容 scikit-learn 的变换器和估计器
- 流程集成实现简化工作流
- 使用分区的集成建模（投票、堆叠）
- 高级交叉验证和超参数调优

主要组件：

- `PartitionTransformer`：基于特征值分区数据的变换器，支持 random_state 参数以确保聚类结果的可重现性
- `AdaptivePartitionRegressor`：用于自适应分区的元估计器
- `PolyPartitionPipeline`：结合多项式特征与分区的管道
- 创建集成和堆叠模型的辅助函数

### plot_utils.py

- 模型性能可视化
- 不同分区策略的比较
- 回归报告生成
- 使用 plotly 支持的交互式图表生成

### stats_utils.py

- 回归统计计算
- 误差指标计算
- 模型比较的统计测试
- 异常值检测和分析

### data_utils.py

- 从各种源加载数据的函数
- 数据预处理工具
- 用于测试和验证的合成数据生成
- 交叉验证数据分割

### io.py

- 模型序列化和反序列化
- 将模型导出为 C++ 部署的 JSON 格式
- 从 JSON 格式导入模型
- 模型版本管理

### ascii_utils.py

- 从列标签和行数据生成和打印 ASCII 表格的工具
- 控制台输出的格式化选项
- 进度条实现

### model_predict_utils.py

- 保存、加载和预测回归模型的工具
- 支持预测管道中的变换器
- 大型数据集的批量预测工具

### cpp_export.py

- 将模型导出为 C++ 格式的工具
- C++ 模型实现的代码生成
- 跨语言测试工具

## 使用示例

### 基本 RegressionFlow API

```python
from fit_better import RegressionFlow, PartitionMode, RegressorType

# 初始化回归流程
flow = RegressionFlow()

# 寻找最佳回归策略
result = flow.find_best_strategy(
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    partition_mode=PartitionMode.KMEANS,
    regressor_type=RegressorType.AUTO,
    n_partitions=5,
    n_jobs=-1
)

# 进行预测
predictions = flow.predict(X_new)

# 导出模型用于 C++ 部署
from fit_better.io import export_model_to_json
export_model_to_json(result.best_model, "best_model.json")
```

### 增强的 scikit-learn API

```python
from fit_better.sklearn_utils import AdaptivePartitionRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# 创建兼容 sklearn 的管道
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('regressor', AdaptivePartitionRegressor(
        n_partitions=5,
        partition_mode='kmeans',
        regressor_type='xgboost',
        n_jobs=-1
    ))
])

# 使用 sklearn API 拟合和预测
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

### 集成方法

```python
from fit_better.sklearn_utils import create_ensemble_model

# 创建结合多种分区策略的集成模型
ensemble = create_ensemble_model(
    X_train, y_train,
    n_partitions=5,
    partition_modes=['kmeans', 'percentile', 'equal_width'],
    regressor_types=['lightgbm', 'random_forest'],
    n_jobs=-1
)

# 使用集成模型进行预测
predictions = ensemble.predict(X_test)
```

## C++ 部署与跨语言测试

本包包含核心回归算法和预处理的 C++ 实现。C++ 部署通过 CMake 管理，单元测试基于 Google Test (GTest)。跨语言测试比较 Python 和 C++ 结果以确保一致性。

### C++ 构建与测试

1. 安装依赖：CMake、GTest、Boost 和 C++17 编译器。
2. 构建 C++ 项目：

   ```bash
   cd cpp
   mkdir -p build && cd build
   cmake ..
   make
   ```

3. 运行 C++ 单元测试：

   ```bash
   ctest
   # 或
   ./tests/fit_better_tests
   ```

4. 从 Python 运行跨语言部署检查：

   ```bash
   python tests/custom/test_cpp_deployment.py
   ```

## 文档

完整的 API 文档可在 [https://fit-better.readthedocs.io](https://fit-better.readthedocs.io) 获取

## 许可证

本项目采用专有许可证。有关许可详情，请联系作者。