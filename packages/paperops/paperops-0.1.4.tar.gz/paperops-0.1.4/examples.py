"""
Example usage of the draw-paper library for academic plotting.

This script demonstrates how to create various types of academic plots
using different templates and color schemes.
"""

import pandas as pd
import numpy as np
from src.paperops.figure.core import AcademicPlotter


def create_sample_data():
    """Create sample data for demonstrations."""
    # Time series data for line plots
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    line_data = pd.DataFrame(
        {
            "date": dates,
            "method_a": np.cumsum(np.random.randn(50)) + 100,
            "method_b": np.cumsum(np.random.randn(50)) + 98,
            "method_c": np.cumsum(np.random.randn(50)) + 102,
        }
    )

    # Categorical data for bar plots
    bar_data = pd.DataFrame(
        {
            "algorithm": ["Algorithm A", "Algorithm B", "Algorithm C", "Algorithm D"],
            "accuracy": [0.85, 0.92, 0.78, 0.89],
            "f1_score": [0.83, 0.90, 0.76, 0.87],
            "precision": [0.81, 0.88, 0.74, 0.85],
        }
    )

    # Grouped bar chart data
    grouped_bar_data = pd.DataFrame(
        {
            "categories": ["Dataset A", "Dataset B", "Dataset C", "Dataset D"],
            "method_1": [23, 45, 56, 78],
            "method_2": [20, 35, 42, 65],
            "method_3": [18, 30, 48, 70],
        }
    )

    # Scatter plot data
    scatter_data = pd.DataFrame(
        {
            "training_time": np.random.exponential(2, 100),
            "accuracy": 0.5 + 0.4 * np.random.beta(2, 2, 100),
            "model_size": np.random.lognormal(0, 1, 100),
            "dataset": np.random.choice(["Dataset A", "Dataset B", "Dataset C"], 100),
        }
    )

    # Correlation matrix for heatmap
    correlation_data = np.random.randn(6, 6)
    correlation_data = np.corrcoef(correlation_data)
    correlation_df = pd.DataFrame(
        correlation_data,
        index=[
            "Feature 1",
            "Feature 2",
            "Feature 3",
            "Feature 4",
            "Feature 5",
            "Feature 6",
        ],
        columns=[
            "Feature 1",
            "Feature 2",
            "Feature 3",
            "Feature 4",
            "Feature 5",
            "Feature 6",
        ],
    )

    return line_data, bar_data, scatter_data, correlation_df, grouped_bar_data


def create_ylim_test_data():
    """Create test data for y-axis limit demonstrations."""

    # Percentage data (0-1 range)
    percentage_data = pd.DataFrame(
        {
            "method": ["Method A", "Method B", "Method C", "Method D"],
            "accuracy": [0.85, 0.92, 0.78, 0.89],
            "precision": [0.83, 0.90, 0.76, 0.87],
            "recall": [0.81, 0.88, 0.74, 0.85],
        }
    )

    # Large scale data
    large_scale_data = pd.DataFrame(
        {
            "categories": ["Cat A", "Cat B", "Cat C", "Cat D"],
            "metric_1": [1200, 1800, 900, 1500],
            "metric_2": [1100, 1650, 850, 1400],
        }
    )

    # Time series data for ylim testing
    np.random.seed(123)  # Different seed for variety
    dates = pd.date_range("2024-01-01", periods=20, freq="D")
    ylim_time_data = pd.DataFrame(
        {
            "date": dates,
            "performance": 95 + np.cumsum(np.random.randn(20) * 0.5),
            "baseline": 90 + np.cumsum(np.random.randn(20) * 0.3),
        }
    )

    return percentage_data, large_scale_data, ylim_time_data


def demo_single_column_plots():
    """Demonstrate single-column plots."""
    print("Creating single-column plots...")

    line_data, bar_data, scatter_data, correlation_df, grouped_bar_data = (
        create_sample_data()
    )

    # Single column plotter with Nature color scheme
    plotter = AcademicPlotter(layout="single", size="medium", color_scheme="nature")

    # Line plot
    fig, ax = plotter.line_plot(
        data=line_data,
        x="date",
        y=["method_a", "method_b", "method_c"],
        fig_name="Performance Comparison Over Time",
        xlabel="Date",
        ylabel="Performance Score",
        save_path="figs/single_line_plot.pdf",
    )
    print("✓ Line plot saved as single_line_plot.pdf")

    # Bar plot
    fig, ax = plotter.bar_plot(
        data=bar_data,
        x="algorithm",
        y="accuracy",
        fig_name="Algorithm Accuracy Comparison",
        xlabel="Algorithm",
        ylabel="Accuracy",
        save_path="figs/single_bar_plot.pdf",
    )
    print("✓ Bar plot saved as single_bar_plot.pdf")

    # Grouped bar plot
    fig, ax = plotter.bar_plot(
        data=grouped_bar_data,
        x="categories",
        y=["method_1", "method_2", "method_3"],
        fig_name="Method Comparison Across Datasets",
        xlabel="Dataset",
        ylabel="Performance Score",
        legend=True,
        save_path="figs/single_grouped_bar_plot.pdf",
    )
    print("✓ Grouped bar plot saved as single_grouped_bar_plot.pdf")

    # Scatter plot
    fig, ax = plotter.scatter_plot(
        data=scatter_data,
        x="training_time",
        y="accuracy",
        size="model_size",
        fig_name="Training Time vs Accuracy",
        xlabel="Training Time (hours)",
        ylabel="Accuracy",
        save_path="figs/single_scatter_plot.pdf",
    )
    print("✓ Scatter plot saved as single_scatter_plot.pdf")


def demo_double_column_plots():
    """Demonstrate double-column plots."""
    print("\nCreating double-column plots...")

    line_data, bar_data, scatter_data, correlation_df, grouped_bar_data = (
        create_sample_data()
    )

    # Double column plotter with Science color scheme
    plotter = AcademicPlotter(layout="double", size="medium", color_scheme="science")

    # Heatmap
    fig, ax = plotter.heatmap(
        data=correlation_df,
        fig_name="Feature Correlation Matrix",
        cmap="RdBu_r",
        annot=True,
        fmt=".2f",
        save_path="figs/double_heatmap.pdf",
    )
    print("✓ Heatmap saved as double_heatmap.pdf")

    # Pie chart
    pie_data = {
        "Deep Learning": 35,
        "Traditional ML": 25,
        "Statistical Methods": 20,
        "Other": 20,
    }
    fig, ax = plotter.pie_chart(
        data=pie_data,
        fig_name="Research Method Distribution",
        save_path="figs/double_pie_chart.pdf",
    )
    print("✓ Pie chart saved as double_pie_chart.pdf")


def demo_color_schemes():
    """Demonstrate different color schemes."""
    print("\nDemonstrating different color schemes...")

    line_data, _, _, _, _ = create_sample_data()

    schemes = ["nature", "science", "ieee", "academic", "colorblind"]

    for scheme in schemes:
        plotter = AcademicPlotter(layout="single", size="small", color_scheme=scheme)

        fig, ax = plotter.line_plot(
            data=line_data.head(20),  # Use fewer data points for clarity
            x="date",
            y=["method_a", "method_b", "method_c"],
            fig_name=f"{scheme.title()} Color Scheme",
            xlabel="Date",
            ylabel="Score",
            save_path=f"figs/color_scheme_{scheme}.pdf",
        )
        print(f"✓ {scheme.title()} color scheme plot saved")


def demo_size_variations():
    """Demonstrate different figure sizes."""
    print("\nDemonstrating different figure sizes...")

    line_data, _, _, _, _ = create_sample_data()

    sizes = ["small", "medium", "large"]

    for size in sizes:
        plotter = AcademicPlotter(layout="single", size=size, color_scheme="academic")

        fig, ax = plotter.line_plot(
            data=line_data.head(15),
            x="date",
            y="method_a",
            fig_name=f"Single Column - {size.title()} Size",
            xlabel="Date",
            ylabel="Score",
            save_path=f"figs/size_single_{size}.pdf",
        )

        info = plotter.get_template_info()
        print(
            f"✓ {size.title()} size plot saved - {info['width_inches']}\" × {info['height_inches']}\""
        )


def demo_grouped_bar_plots():
    """Demonstrate grouped bar plot functionality."""
    print("\nDemonstrating grouped bar plots...")

    # Create sample data for grouped bar charts
    performance_data = pd.DataFrame(
        {
            "algorithms": ["SVM", "Random Forest", "Neural Network", "XGBoost"],
            "accuracy": [0.85, 0.92, 0.89, 0.94],
            "precision": [0.83, 0.90, 0.87, 0.92],
            "recall": [0.81, 0.88, 0.85, 0.90],
        }
    )

    comparison_data = pd.DataFrame(
        {
            "datasets": ["MNIST", "CIFAR-10", "ImageNet", "COCO"],
            "baseline": [85.2, 72.1, 65.8, 45.3],
            "proposed_method": [92.7, 78.9, 71.2, 52.6],
            "sota": [94.1, 82.3, 74.5, 55.8],
        }
    )

    plotter = AcademicPlotter(layout="single", size="medium", color_scheme="science")

    # Single metric comparison
    fig, ax = plotter.bar_plot(
        data=performance_data,
        x="algorithms",
        y="accuracy",
        fig_name="Single Metric: Algorithm Accuracy",
        xlabel="Algorithms",
        ylabel="Accuracy",
        save_path="figs/grouped_single_metric.pdf",
    )
    print("✓ Single metric bar plot saved as grouped_single_metric.pdf")

    # Multiple metrics comparison (grouped bars)
    fig, ax = plotter.bar_plot(
        data=performance_data,
        x="algorithms",
        y=["accuracy", "precision", "recall"],
        fig_name="Multi-Metric Algorithm Comparison",
        xlabel="Algorithms",
        ylabel="Score",
        legend=True,
        save_path="figs/grouped_multi_metric.pdf",
    )
    print("✓ Multi-metric grouped bar plot saved as grouped_multi_metric.pdf")

    # Method comparison across datasets
    fig, ax = plotter.bar_plot(
        data=comparison_data,
        x="datasets",
        y=["baseline", "proposed_method", "sota"],
        fig_name="Method Comparison Across Datasets",
        xlabel="Datasets",
        ylabel="Performance (%)",
        legend=True,
        save_path="figs/grouped_method_comparison.pdf",
    )
    print("✓ Method comparison grouped bar plot saved as grouped_method_comparison.pdf")

    # Horizontal grouped bar chart
    plotter_horizontal = AcademicPlotter(
        layout="double", size="medium", color_scheme="nature"
    )

    fig, ax = plotter_horizontal.bar_plot(
        data=comparison_data,
        x="datasets",
        y=["baseline", "proposed_method"],
        fig_name="Horizontal Method Comparison",
        xlabel="Performance (%)",
        ylabel="Datasets",
        horizontal=True,
        legend=True,
        save_path="figs/grouped_horizontal_comparison.pdf",
    )
    print("✓ Horizontal grouped bar plot saved as grouped_horizontal_comparison.pdf")


def demo_ylim_modes():
    """Demonstrate different y-axis limit modes."""
    print("\nDemonstrating Y-axis Limit Modes...")

    percentage_data, large_scale_data, ylim_time_data = create_ylim_test_data()

    # Create plotter
    plotter = AcademicPlotter(layout="single", size="medium", color_scheme="science")

    # Test 1: Auto mode (default)
    fig, ax = plotter.bar_plot(
        data=percentage_data,
        x="method",
        y="accuracy",
        fig_name="Auto Y-axis Limits",
        ylabel="Accuracy",
        ylim_mode="auto",
        save_path="figs/ylim_auto.pdf",
    )
    print("✓ Auto mode plot saved as ylim_auto.pdf")

    # Test 2: Percentage mode (0 to 1)
    fig, ax = plotter.bar_plot(
        data=percentage_data,
        x="method",
        y="accuracy",
        fig_name="Percentage Y-axis Limits (0-1)",
        ylabel="Accuracy",
        ylim_mode="percentage",
        save_path="figs/ylim_percentage.pdf",
    )
    print("✓ Percentage mode plot saved as ylim_percentage.pdf")

    # Test 3: Data extend mode (min to max*1.1)
    fig, ax = plotter.bar_plot(
        data=large_scale_data,
        x="categories",
        y="metric_1",
        fig_name="Data Extend Y-axis Limits",
        ylabel="Value",
        ylim_mode="data_extend",
        save_path="figs/ylim_data_extend.pdf",
    )
    print("✓ Data extend mode plot saved as ylim_data_extend.pdf")

    # Test 4: Zero extend mode (0 to max*1.1)
    fig, ax = plotter.bar_plot(
        data=large_scale_data,
        x="categories",
        y="metric_1",
        fig_name="Zero Extend Y-axis Limits",
        ylabel="Value",
        ylim_mode="zero_extend",
        save_path="figs/ylim_zero_extend.pdf",
    )
    print("✓ Zero extend mode plot saved as ylim_zero_extend.pdf")

    # Test 5: Custom mode
    fig, ax = plotter.bar_plot(
        data=large_scale_data,
        x="categories",
        y="metric_1",
        fig_name="Custom Y-axis Limits (500-2000)",
        ylabel="Value",
        ylim_mode="custom",
        ylim=(500, 2000),
        save_path="figs/ylim_custom.pdf",
    )
    print("✓ Custom mode plot saved as ylim_custom.pdf")

    # Test 6: Grouped bars with percentage mode
    fig, ax = plotter.bar_plot(
        data=percentage_data,
        x="method",
        y=["accuracy", "precision", "recall"],
        fig_name="Grouped Bars with Percentage Limits",
        ylabel="Score",
        ylim_mode="percentage",
        legend=True,
        save_path="figs/ylim_grouped_percentage.pdf",
    )
    print(
        "✓ Grouped bars with percentage mode plot saved as ylim_grouped_percentage.pdf"
    )

    # Test 7: Line plot with data extend mode
    fig, ax = plotter.line_plot(
        data=ylim_time_data,
        x="date",
        y=["performance", "baseline"],
        fig_name="Line Plot with Data Extend Limits",
        xlabel="Date",
        ylabel="Performance Score",
        ylim_mode="data_extend",
        save_path="figs/ylim_line_data_extend.pdf",
    )
    print("✓ Line plot with data extend mode plot saved as ylim_line_data_extend.pdf")


if __name__ == "__main__":
    print("Draw Paper Library - Academic Plotting Examples")
    print("=" * 50)

    # Run demonstrations
    demo_single_column_plots()
    demo_double_column_plots()
    demo_grouped_bar_plots()
    demo_color_schemes()
    demo_size_variations()
    demo_ylim_modes()

    print("\n" + "=" * 50)
    print("All example plots have been generated!")
    print("Check the current directory for PDF files.")
