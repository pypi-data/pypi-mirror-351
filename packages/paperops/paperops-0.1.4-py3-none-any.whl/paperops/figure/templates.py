"""
Template classes for academic paper plotting.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt

from .config import (
    FigureSize,
    FIGURE_DIMENSIONS,
    FONT_SIZES,
    ACADEMIC_STYLE,
    CustomConfig,
)
from .styles import ColorScheme, get_color_scheme, get_plot_style


class Template(ABC):
    """Abstract base class for plotting templates."""

    def __init__(
        self,
        figure_size: FigureSize,
        color_scheme: ColorScheme = ColorScheme.ACADEMIC,
        custom_config: Optional[CustomConfig] = None,
    ):
        """
        Initialize template.

        Parameters:
        -----------
        figure_size : FigureSize
            Size configuration for the figure
        color_scheme : ColorScheme
            Color scheme to use for plots
        custom_config : CustomConfig, optional
            Custom configuration to override defaults
        """
        self.figure_size = figure_size
        self.color_scheme = color_scheme
        self.custom_config = custom_config

        # Use custom config if provided, otherwise use defaults
        if custom_config:
            self.dimensions = custom_config.get_figure_dimensions(figure_size)
            self.font_sizes = custom_config.get_font_sizes(figure_size)
            self.academic_style = custom_config.get_academic_style()
        else:
            self.dimensions = FIGURE_DIMENSIONS[figure_size]
            self.font_sizes = FONT_SIZES[figure_size]
            self.academic_style = ACADEMIC_STYLE

    def apply_style(self, plot_type: str = "line") -> None:
        """Apply academic style settings to matplotlib."""
        # Apply base academic style (from custom config or default)
        plt.style.use("default")  # Reset to default first
        plt.rcParams.update(self.academic_style)

        # Apply font sizes
        plt.rcParams.update(
            {
                "font.size": self.font_sizes["label"],
                "axes.titlesize": self.font_sizes["title"],
                "axes.labelsize": self.font_sizes["label"],
                "xtick.labelsize": self.font_sizes["tick"],
                "ytick.labelsize": self.font_sizes["tick"],
                "legend.fontsize": self.font_sizes["legend"],
            }
        )

        # Apply plot-specific styles
        plot_style = get_plot_style(plot_type)
        plt.rcParams.update(plot_style)

    def create_figure(self, **kwargs) -> tuple:
        """
        Create a figure with the template settings.

        Returns:
        --------
        tuple
            (figure, axes) objects
        """
        fig, ax = plt.subplots(figsize=self.dimensions, **kwargs)
        return fig, ax

    def get_colors(self, n_colors: Optional[int] = None) -> list:
        """Get colors from the template's color scheme."""
        return get_color_scheme(self.color_scheme, n_colors)

    @abstractmethod
    def get_layout_info(self) -> Dict[str, Any]:
        """Get layout-specific information."""
        pass


class SingleColumn(Template):
    """Template for single-column figures in academic papers."""

    def __init__(
        self,
        size: str = "medium",
        color_scheme: ColorScheme = ColorScheme.ACADEMIC,
        custom_config: Optional[CustomConfig] = None,
    ):
        """
        Initialize single-column template.

        Parameters:
        -----------
        size : str
            Size variant ('small', 'medium', 'large')
        color_scheme : ColorScheme
            Color scheme to use
        custom_config : CustomConfig, optional
            Custom configuration to override defaults
        """
        size_map = {
            "small": FigureSize.SINGLE_SMALL,
            "medium": FigureSize.SINGLE_MEDIUM,
            "large": FigureSize.SINGLE_LARGE,
        }

        if size not in size_map:
            raise ValueError(f"Size must be one of {list(size_map.keys())}")

        super().__init__(size_map[size], color_scheme, custom_config)

    def get_layout_info(self) -> Dict[str, Any]:
        """Get single-column layout information."""
        return {
            "layout": "single_column",
            "width_inches": self.dimensions[0],
            "height_inches": self.dimensions[1],
            "recommended_dpi": 300,
            "text_width_ratio": 1.0,  # Uses full text width
        }


class DoubleColumn(Template):
    """Template for double-column (full-width) figures in academic papers."""

    def __init__(
        self,
        size: str = "medium",
        color_scheme: ColorScheme = ColorScheme.ACADEMIC,
        custom_config: Optional[CustomConfig] = None,
    ):
        """
        Initialize double-column template.

        Parameters:
        -----------
        size : str
            Size variant ('small', 'medium', 'large')
        color_scheme : ColorScheme
            Color scheme to use
        custom_config : CustomConfig, optional
            Custom configuration to override defaults
        """
        size_map = {
            "small": FigureSize.DOUBLE_SMALL,
            "medium": FigureSize.DOUBLE_MEDIUM,
            "large": FigureSize.DOUBLE_LARGE,
        }

        if size not in size_map:
            raise ValueError(f"Size must be one of {list(size_map.keys())}")

        super().__init__(size_map[size], color_scheme, custom_config)

    def get_layout_info(self) -> Dict[str, Any]:
        """Get double-column layout information."""
        return {
            "layout": "double_column",
            "width_inches": self.dimensions[0],
            "height_inches": self.dimensions[1],
            "recommended_dpi": 300,
            "text_width_ratio": 2.0,  # Uses full page width
        }
