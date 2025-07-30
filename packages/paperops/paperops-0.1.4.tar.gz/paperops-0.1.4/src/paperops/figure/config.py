"""
Configuration settings for academic paper plotting templates.
"""

from enum import Enum
from typing import Any, Dict, Tuple, Optional
import copy


class PageLayout(Enum):
    """Page layout types for academic papers."""

    SINGLE_COLUMN = "single_column"
    DOUBLE_COLUMN = "double_column"


class LegendStyle(Enum):
    """Legend style options for academic papers."""

    CLEAN = "clean"  # No background, no frame (default academic style)
    GRAY_TRANSPARENT = "gray_transparent"  # Gray transparent background
    WHITE_FRAME = "white_frame"  # White background with frame
    MINIMAL = "minimal"  # Minimal styling


class FigureSize(Enum):
    """Standard figure sizes for academic papers (in inches)."""

    # Single column sizes
    SINGLE_SMALL = "single_small"  # 3.5 x 2.6
    SINGLE_MEDIUM = "single_medium"  # 3.5 x 3.5
    SINGLE_LARGE = "single_large"  # 3.5 x 4.5

    # Double column sizes
    DOUBLE_SMALL = "double_small"  # 7.0 x 3.0
    DOUBLE_MEDIUM = "double_medium"  # 7.0 x 4.5
    DOUBLE_LARGE = "double_large"  # 7.0 x 6.0


# Figure dimensions mapping (width, height) in inches
# Optimized for academic papers with proper aspect ratios
FIGURE_DIMENSIONS: Dict[FigureSize, Tuple[float, float]] = {
    # Single column - typical text width is 3.3-3.5 inches
    FigureSize.SINGLE_SMALL: (3.5, 2.2),  # ~1.6:1 ratio (golden ratio)
    FigureSize.SINGLE_MEDIUM: (3.5, 2.6),  # ~1.35:1 ratio
    FigureSize.SINGLE_LARGE: (3.5, 2.8),
    # Double column - typical text width is 6.5-7.0 inches
    FigureSize.DOUBLE_SMALL: (7.0, 3.5),  # 2:1 ratio (good for wide charts)
    FigureSize.DOUBLE_MEDIUM: (7.0, 4.4),  # ~1.6:1 ratio (golden ratio)
    FigureSize.DOUBLE_LARGE: (7.0, 5.0),  # ~1.4:1 ratio
}

# Font sizes for different layouts and figure sizes
FONT_SIZES: Dict[FigureSize, Dict[str, int]] = {
    FigureSize.SINGLE_SMALL: {
        "title": 10,
        "label": 8,
        "tick": 7,
        "legend": 7,
    },
    FigureSize.SINGLE_MEDIUM: {
        "title": 11,
        "label": 9,
        "tick": 8,
        "legend": 8,
    },
    FigureSize.SINGLE_LARGE: {
        "title": 12,
        "label": 10,
        "tick": 9,
        "legend": 9,
    },
    FigureSize.DOUBLE_SMALL: {
        "title": 12,
        "label": 10,
        "tick": 9,
        "legend": 9,
    },
    FigureSize.DOUBLE_MEDIUM: {
        "title": 14,
        "label": 12,
        "tick": 10,
        "legend": 10,
    },
    FigureSize.DOUBLE_LARGE: {
        "title": 16,
        "label": 14,
        "tick": 12,
        "legend": 12,
    },
}

# Default matplotlib settings for academic papers
ACADEMIC_STYLE = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Computer Modern Roman"],
    "text.usetex": False,  # Set to True if LaTeX is available
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.major.size": 4,
    "xtick.minor.size": 2,
    "ytick.major.size": 4,
    "ytick.minor.size": 2,
    "legend.frameon": False,
    "legend.numpoints": 1,
    "legend.scatterpoints": 1,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
}

# Legend style configurations
LEGEND_STYLES: Dict[LegendStyle, Dict[str, Any]] = {
    LegendStyle.CLEAN: {
        "frameon": False,
        "fancybox": False,
        "shadow": False,
        "framealpha": 0.0,
        "facecolor": "none",
        "edgecolor": "none",
    },
    LegendStyle.GRAY_TRANSPARENT: {
        "frameon": True,
        "fancybox": False,
        "shadow": False,
        "framealpha": 0.8,
        "facecolor": "lightgray",
        "edgecolor": "none",
    },
    LegendStyle.WHITE_FRAME: {
        "frameon": True,
        "fancybox": False,
        "shadow": False,
        "framealpha": 0.9,
        "facecolor": "white",
        "edgecolor": "black",
    },
    LegendStyle.MINIMAL: {
        "frameon": True,
        "fancybox": False,
        "shadow": False,
        "framealpha": 0.8,
        "facecolor": "white",
        "edgecolor": "none",
    },
}


class CustomConfig:
    """
    Custom configuration class for academic paper plotting.

    This class allows users to create custom themes by modifying default settings
    or creating entirely new configurations.
    """

    def __init__(
        self,
        figure_dimensions: Optional[Dict[FigureSize, Tuple[float, float]]] = None,
        font_sizes: Optional[Dict[FigureSize, Dict[str, int]]] = None,
        academic_style: Optional[Dict[str, Any]] = None,
        legend_styles: Optional[Dict[Any, Dict[str, Any]]] = None,
    ):
        """
        Initialize custom configuration.

        Parameters:
        -----------
        figure_dimensions : dict, optional
            Custom figure dimensions mapping
        font_sizes : dict, optional
            Custom font sizes mapping
        academic_style : dict, optional
            Custom matplotlib style settings
        legend_styles : dict, optional
            Custom legend style configurations (can use LegendStyle enum or string keys)
        """
        # Use provided configurations or default to built-in ones
        self.figure_dimensions = (
            figure_dimensions
            if figure_dimensions is not None
            else copy.deepcopy(FIGURE_DIMENSIONS)
        )
        self.font_sizes = (
            font_sizes if font_sizes is not None else copy.deepcopy(FONT_SIZES)
        )
        self.academic_style = (
            academic_style
            if academic_style is not None
            else copy.deepcopy(ACADEMIC_STYLE)
        )
        # For legend styles, we need to handle both LegendStyle enum and string keys
        if legend_styles is not None:
            self.legend_styles: Dict[Any, Dict[str, Any]] = copy.deepcopy(legend_styles)
        else:
            self.legend_styles: Dict[Any, Dict[str, Any]] = copy.deepcopy(LEGEND_STYLES)

    @classmethod
    def from_default(cls) -> "CustomConfig":
        """
        Create a custom config based on default settings.

        Returns:
        --------
        CustomConfig
            A new CustomConfig instance with default settings that can be modified
        """
        return cls()

    def copy(self) -> "CustomConfig":
        """
        Create a deep copy of this configuration.

        Returns:
        --------
        CustomConfig
            A copy of this configuration
        """
        return CustomConfig(
            figure_dimensions=copy.deepcopy(self.figure_dimensions),
            font_sizes=copy.deepcopy(self.font_sizes),
            academic_style=copy.deepcopy(self.academic_style),
            legend_styles=copy.deepcopy(self.legend_styles),
        )

    def update_figure_dimensions(
        self, size: FigureSize, width: float, height: float
    ) -> None:
        """
        Update figure dimensions for a specific size.

        Parameters:
        -----------
        size : FigureSize
            The figure size to update
        width : float
            New width in inches
        height : float
            New height in inches
        """
        self.figure_dimensions[size] = (width, height)

    def update_font_sizes(self, size: FigureSize, **font_sizes: int) -> None:
        """
        Update font sizes for a specific figure size.

        Parameters:
        -----------
        size : FigureSize
            The figure size to update
        **font_sizes : int
            Font sizes to update (title, label, tick, legend)
        """
        if size not in self.font_sizes:
            self.font_sizes[size] = {}

        for font_type, font_size in font_sizes.items():
            self.font_sizes[size][font_type] = font_size

    def update_academic_style(self, **style_params: Any) -> None:
        """
        Update academic style parameters.

        Parameters:
        -----------
        **style_params : Any
            Matplotlib style parameters to update
        """
        self.academic_style.update(style_params)

    def add_legend_style(self, name: Any, style_config: Dict[str, Any]) -> None:
        """
        Add a new legend style or update an existing one.

        Parameters:
        -----------
        name : Any
            Name of the legend style (can be string or LegendStyle enum)
        style_config : dict
            Legend style configuration
        """
        # Store custom styles with string or enum keys
        self.legend_styles[name] = style_config

    def get_figure_dimensions(self, size: FigureSize) -> Tuple[float, float]:
        """Get figure dimensions for a specific size."""
        return self.figure_dimensions.get(size, FIGURE_DIMENSIONS[size])

    def get_font_sizes(self, size: FigureSize) -> Dict[str, int]:
        """Get font sizes for a specific figure size."""
        return self.font_sizes.get(size, FONT_SIZES[size])

    def get_academic_style(self) -> Dict[str, Any]:
        """Get academic style configuration."""
        return self.academic_style

    def get_legend_styles(self) -> Dict[Any, Dict[str, Any]]:
        """Get legend style configurations."""
        return self.legend_styles


def create_custom_config_from_default() -> CustomConfig:
    """
    Create a custom configuration based on default settings.

    This is a convenience function for users who want to start with
    default settings and then customize them.

    Returns:
    --------
    CustomConfig
        A new CustomConfig instance with default settings

    Example:
    --------
    >>> config = create_custom_config_from_default()
    >>> config.update_academic_style(font_family="sans-serif")
    >>> config.update_font_sizes(FigureSize.SINGLE_MEDIUM, title=12, label=10)
    """
    return CustomConfig.from_default()


def create_ieee_style_config() -> CustomConfig:
    """
    Create an IEEE style configuration.

    Returns:
    --------
    CustomConfig
        Configuration optimized for IEEE publications
    """
    config = CustomConfig.from_default()

    # IEEE preferences - typically more technical/engineering style
    config.update_academic_style(
        **{
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Computer Modern Roman"],
            "axes.linewidth": 0.8,
            "grid.alpha": 0.3,
            "axes.grid": True,
        }
    )

    return config
