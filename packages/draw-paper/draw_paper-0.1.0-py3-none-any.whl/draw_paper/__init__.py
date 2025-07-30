"""
Draw Paper - A specialized plotting library for academic papers.

This library provides LaTeX-compatible templates and styles for creating
publication-ready figures with minimal configuration.
"""

from .core import AcademicPlotter
from .templates import Template, SingleColumn, DoubleColumn
from .styles import ColorScheme, get_color_scheme

__version__ = "0.1.0"
__all__ = [
    "AcademicPlotter",
    "Template",
    "SingleColumn",
    "DoubleColumn",
    "ColorScheme",
    "get_color_scheme",
]
