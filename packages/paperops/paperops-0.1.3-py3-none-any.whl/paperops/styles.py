"""
Color schemes and styling for academic paper plots.
"""

from enum import Enum
from typing import List, Dict, Any, Optional


class ColorScheme(Enum):
    """Predefined color schemes for different plot types."""

    # Professional color schemes
    NATURE = "nature"  # Nature journal style
    SCIENCE = "science"  # Science journal style
    IEEE = "ieee"  # IEEE publication style
    ACADEMIC = "academic"  # General academic style

    # Specific plot type schemes
    QUALITATIVE = "qualitative"  # For categorical data
    SEQUENTIAL = "sequential"  # For continuous data
    DIVERGING = "diverging"  # For data with meaningful center

    # Accessibility
    COLORBLIND = "colorblind"  # Colorblind-friendly palette


# Color palettes for different schemes
COLOR_PALETTES: Dict[ColorScheme, List[str]] = {
    ColorScheme.NATURE: [
        "#1f77b4",  # Blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#7f7f7f",  # Gray
    ],
    ColorScheme.SCIENCE: [
        "#0173B2",  # Blue
        "#DE8F05",  # Orange
        "#029E73",  # Green
        "#D55E00",  # Red
        "#CC78BC",  # Pink
        "#CA9161",  # Brown
        "#FBAFE4",  # Light pink
        "#949494",  # Gray
    ],
    ColorScheme.IEEE: [
        "#1E88E5",  # Blue
        "#FFC107",  # Amber
        "#4CAF50",  # Green
        "#F44336",  # Red
        "#9C27B0",  # Purple
        "#FF9800",  # Orange
        "#607D8B",  # Blue gray
        "#795548",  # Brown
    ],
    ColorScheme.ACADEMIC: [
        "#2E86AB",  # Blue
        "#A23B72",  # Magenta
        "#F18F01",  # Orange
        "#C73E1D",  # Red
        "#592E83",  # Purple
        "#1B998B",  # Teal
        "#84A59D",  # Sage
        "#F28482",  # Pink
    ],
    ColorScheme.QUALITATIVE: [
        "#E69F00",  # Orange
        "#56B4E9",  # Sky blue
        "#009E73",  # Bluish green
        "#F0E442",  # Yellow
        "#0072B2",  # Blue
        "#D55E00",  # Vermillion
        "#CC79A7",  # Reddish purple
        "#999999",  # Gray
    ],
    ColorScheme.SEQUENTIAL: [
        "#FFF7EC",  # Light
        "#FEE8C8",
        "#FDD49E",
        "#FDBB84",
        "#FC8D59",
        "#EF6548",
        "#D7301F",
        "#B30000",  # Dark
    ],
    ColorScheme.DIVERGING: [
        "#8E0152",  # Dark red
        "#C51B7D",  # Red
        "#DE77AE",  # Pink
        "#F1B6DA",  # Light pink
        "#FDE0EF",  # Very light pink
        "#E6F5D0",  # Very light green
        "#B8E186",  # Light green
        "#7FBC41",  # Green
        "#4D9221",  # Dark green
        "#276419",  # Very dark green
    ],
    ColorScheme.COLORBLIND: [
        "#000000",  # Black
        "#E69F00",  # Orange
        "#56B4E9",  # Sky blue
        "#009E73",  # Bluish green
        "#F0E442",  # Yellow
        "#0072B2",  # Blue
        "#D55E00",  # Vermillion
        "#CC79A7",  # Reddish purple
    ],
}


def get_color_scheme(scheme: ColorScheme, n_colors: Optional[int] = None) -> List[str]:
    """
    Get colors from a specified color scheme.

    Parameters:
    -----------
    scheme : ColorScheme
        The color scheme to use
    n_colors : int, optional
        Number of colors to return. If None, returns all colors in scheme.

    Returns:
    --------
    List[str]
        List of hex color codes
    """
    colors = COLOR_PALETTES[scheme]

    if n_colors is None:
        return colors

    if n_colors <= len(colors):
        return colors[:n_colors]
    else:
        # If more colors needed than available, cycle through the palette
        return (colors * ((n_colors // len(colors)) + 1))[:n_colors]


def get_plot_style(plot_type: str) -> Dict[str, Any]:
    """
    Get matplotlib style parameters for specific plot types.

    Parameters:
    -----------
    plot_type : str
        Type of plot ('line', 'bar', 'scatter', 'pie', etc.)

    Returns:
    --------
    Dict[str, Any]
        Style parameters for matplotlib
    """
    base_style = {
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.5,
    }

    plot_specific = {
        "line": {
            "lines.linewidth": 1.5,
            "lines.markersize": 4,
            "axes.grid": True,
        },
        "bar": {
            "axes.grid": False,
            "axes.axisbelow": True,
        },
        "scatter": {
            "lines.markersize": 6,
            "axes.grid": True,
        },
        "pie": {
            "axes.grid": False,
        },
        "heatmap": {
            "axes.grid": False,
        },
        "box": {
            "axes.grid": True,
            "axes.axisbelow": True,
        },
        "violin": {
            "axes.grid": True,
            "axes.axisbelow": True,
        },
    }

    style = base_style.copy()
    if plot_type in plot_specific:
        style.update(plot_specific[plot_type])

    return style
