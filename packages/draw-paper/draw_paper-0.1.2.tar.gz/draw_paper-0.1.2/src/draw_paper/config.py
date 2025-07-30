"""
Configuration settings for academic paper plotting templates.
"""

from enum import Enum
from typing import Dict, Tuple


class PageLayout(Enum):
    """Page layout types for academic papers."""

    SINGLE_COLUMN = "single_column"
    DOUBLE_COLUMN = "double_column"


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
