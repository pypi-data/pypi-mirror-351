# PaperOps - Academic Publication-Ready Plotting Library

![Version](https://img.shields.io/badge/version-0.1.3-blue)
![Python](https://img.shields.io/badge/python-3.13+-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)

PaperOps is a Python plotting library specifically designed for academic papers, providing chart templates and styles that meet top-tier journal standards. Whether using single-column or double-column layouts, PaperOps helps researchers quickly create professional and aesthetically pleasing academic figures.

## ✨ Key Features

### 📊 Diverse Chart Types
- **Line Plots**: Time series data and trend analysis
- **Bar Charts**: Single and multi-metric comparisons with grouped and horizontal layouts
- **Scatter Plots**: Correlation analysis with size and color mapping
- **Heatmaps**: Correlation matrices and confusion matrix visualization
- **Pie Charts**: Proportion distribution display

### 🎨 Professional Color Schemes
- **Nature**: Nature journal style colors
- **Science**: Science journal style colors
- **IEEE**: IEEE publication standard colors
- **Academic**: General academic style colors
- **Colorblind**: Colorblind-friendly color palette

### 📐 Flexible Layout Templates
- **Single Column Layout**: Suitable for most journal single-column figures
- **Double Column Layout**: Suitable for large figures spanning two columns
- **Multiple Sizes**: Small, Medium, Large

### 🔧 Smart Features
- **Automatic Y-axis Limits**: Multiple modes (auto, percentage, data_extend, zero_extend, custom)
- **Smart Legend Positioning**: Automatically finds optimal legend placement to avoid data overlap
- **High-Quality Output**: Automatically optimizes DPI and font sizes for print quality

## 🚀 Quick Start

### Installation

```bash
pip install paperops

# or

uv add paperops
```

### Basic Usage

```python
import pandas as pd
import numpy as np
from paperops.core import AcademicPlotter

# Create sample data
data = pd.DataFrame({
    'x': range(10),
    'method_a': np.random.rand(10) * 100,
    'method_b': np.random.rand(10) * 100,
    'method_c': np.random.rand(10) * 100
})

# Create plotter
plotter = AcademicPlotter(
    layout="single",           # Single column layout
    size="medium",            # Medium size
    color_scheme="nature"     # Nature journal colors
)

# Create line plot
fig, ax = plotter.line_plot(
    data=data,
    x='x',
    y=['method_a', 'method_b', 'method_c'],
    fig_name="Performance Comparison",
    xlabel="Time Steps",
    ylabel="Performance Score",
    save_path="comparison.pdf"
)
```

## 📚 Detailed Usage Examples

### 1. Bar Chart - Algorithm Performance Comparison

```python
# Single metric comparison
algorithms_data = pd.DataFrame({
    'algorithm': ['SVM', 'Random Forest', 'Neural Network', 'XGBoost'],
    'accuracy': [0.85, 0.92, 0.89, 0.94]
})

plotter = AcademicPlotter(layout="single", color_scheme="science")

fig, ax = plotter.bar_plot(
    data=algorithms_data,
    x='algorithm',
    y='accuracy',
    fig_name="Algorithm Accuracy Comparison",
    xlabel="Algorithm",
    ylabel="Accuracy",
    ylim_mode="percentage",  # Y-axis limited to 0-1
    save_path="algorithm_comparison.pdf"
)
```

### 2. Grouped Bar Chart - Multi-Metric Comparison

```python
# Multi-metric comparison
multi_metrics_data = pd.DataFrame({
    'algorithm': ['SVM', 'Random Forest', 'Neural Network', 'XGBoost'],
    'accuracy': [0.85, 0.92, 0.89, 0.94],
    'precision': [0.83, 0.90, 0.87, 0.92],
    'recall': [0.81, 0.88, 0.85, 0.90]
})

fig, ax = plotter.bar_plot(
    data=multi_metrics_data,
    x='algorithm',
    y=['accuracy', 'precision', 'recall'],
    fig_name="Multi-Metric Algorithm Comparison",
    xlabel="Algorithm",
    ylabel="Score",
    legend=True,
    ylim_mode="percentage",
    save_path="multi_metric_comparison.pdf"
)
```

### 3. Scatter Plot - Training Time vs Accuracy

```python
scatter_data = pd.DataFrame({
    'training_time': np.random.exponential(2, 100),
    'accuracy': 0.5 + 0.4 * np.random.beta(2, 2, 100),
    'model_size': np.random.lognormal(0, 1, 100)
})

fig, ax = plotter.scatter_plot(
    data=scatter_data,
    x='training_time',
    y='accuracy',
    size='model_size',  # Point size mapped to model size
    fig_name="Training Time vs Accuracy",
    xlabel="Training Time (hours)",
    ylabel="Accuracy",
    save_path="time_accuracy_scatter.pdf"
)
```

### 4. Heatmap - Feature Correlation Matrix

```python
# Create correlation matrix
correlation_matrix = np.random.randn(6, 6)
correlation_matrix = np.corrcoef(correlation_matrix)
correlation_df = pd.DataFrame(
    correlation_matrix,
    index=['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Feature 5', 'Feature 6'],
    columns=['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Feature 5', 'Feature 6']
)

plotter = AcademicPlotter(layout="double", color_scheme="science")

fig, ax = plotter.heatmap(
    data=correlation_df,
    fig_name="Feature Correlation Matrix",
    cmap="RdBu_r",
    annot=True,
    fmt=".2f",
    save_path="correlation_heatmap.pdf"
)
```

## 🎯 Advanced Features

### Y-axis Limit Modes

PaperOps provides multiple Y-axis limit modes to adapt to different data types:

```python
# Auto mode (default)
ylim_mode="auto"

# Percentage mode (0-1 or 0-100)
ylim_mode="percentage"

# Data extend mode (min to max*1.1)
ylim_mode="data_extend"

# Zero extend mode (0 to max*1.1)
ylim_mode="zero_extend"

# Custom mode
ylim_mode="custom"
ylim=(0, 100)
```

### Legend Style Control

```python
fig, ax = plotter.line_plot(
    data=data,
    x='x',
    y=['method_a', 'method_b'],
    legend=True,
    legend_location="upper right",  # Specify legend position
    legend_outside=False,           # Whether to place legend outside plot
    legend_style="clean"            # Legend style
)
```

### Color Scheme Switching

```python
# Switch color scheme at runtime
plotter.set_color_scheme("ieee")

# Or specify during initialization
plotter = AcademicPlotter(color_scheme="colorblind")
```

## 📁 Project Structure

```
paperops/
├── core.py          # Main plotting interface
├── plots.py         # Various chart implementations
├── styles.py        # Color schemes and styles
├── templates.py     # Layout templates
└── config.py        # Configuration options
```

## 🎨 Available Color Schemes

| Scheme Name | Description | Use Case |
|-------------|-------------|----------|
| `nature` | Nature journal style | Biology, medical papers |
| `science` | Science journal style | Physics, chemistry papers |
| `ieee` | IEEE standard colors | Engineering, computer science papers |
| `academic` | General academic style | All disciplines |
| `colorblind` | Colorblind-friendly colors | Accessibility considerations |

## 📏 Layout Sizes

| Layout | Small | Medium | Large |
|--------|-------|--------|-------|
| Single Column | 3.5" × 2.6" | 4.5" × 3.4" | 5.5" × 4.1" |
| Double Column | 7.0" × 2.6" | 9.0" × 3.4" | 11.0" × 4.1" |

## 🔧 Dependencies

- Python 3.13+
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- numpy >= 1.24.0
- pandas >= 2.0.0
- scipy >= 1.10.0

## 🤝 Contributing

Issues and Pull Requests are welcome! Before contributing code, please ensure:

1. Code follows PEP 8 standards
2. Add appropriate test cases
3. Update relevant documentation

## 📄 License

This project is licensed under the APACHE 2.0 License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

This repository was generated by Claude 4, aimed at providing high-quality plotting tools for academic researchers to make paper figure creation simpler and more efficient.

---

**Quick Links**: [Installation](#installation) | [Usage Examples](#detailed-usage-examples) | [API Documentation](#key-features) | [Contributing](#contributing)