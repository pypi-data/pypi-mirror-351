"""
Main plotting interface for academic papers.
"""

from typing import Optional, Union, List, Dict, Any
import pandas as pd
import numpy as np
from matplotlib.figure import Figure

from .templates import SingleColumn, DoubleColumn
from .styles import ColorScheme
from .plots import LinePlot, BarPlot, ScatterPlot, PiePlot, HeatmapPlot


class AcademicPlotter:
    """
    Main interface for creating academic publication-ready plots.

    This class provides a simple API for creating various types of plots
    with academic paper styling and templates.
    """

    def __init__(
        self,
        layout: str = "single",
        size: str = "medium",
        color_scheme: Union[str, ColorScheme] = "academic",
    ):
        """
        Initialize the academic plotter.

        Parameters:
        -----------
        layout : str
            Layout type ('single' or 'double')
        size : str
            Figure size ('small', 'medium', 'large')
        color_scheme : str or ColorScheme
            Color scheme to use
        """
        # Convert string to ColorScheme if needed
        if isinstance(color_scheme, str):
            color_scheme = ColorScheme(color_scheme.lower())

        # Create template based on layout
        if layout.lower() == "single":
            self.template = SingleColumn(size, color_scheme)
        elif layout.lower() == "double":
            self.template = DoubleColumn(size, color_scheme)
        else:
            raise ValueError("Layout must be 'single' or 'double'")

        # Initialize plot generators
        self._line_generator = LinePlot(self.template)
        self._bar_generator = BarPlot(self.template)
        self._scatter_generator = ScatterPlot(self.template)
        self._pie_generator = PiePlot(self.template)
        self._heatmap_generator = HeatmapPlot(self.template)

    def line_plot(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        x: str,
        y: Union[str, List[str]],
        fig_name: Optional[str] = None,
        save_path: Optional[str] = None,
        legend_location: Optional[str] = None,
        legend_outside: bool = False,
        ylim_mode: str = "auto",
        ylim: Optional[tuple] = None,
        **kwargs,
    ) -> tuple:
        """
        Create a line plot.

        Parameters:
        -----------
        data : DataFrame or dict
            Data to plot
        x : str
            Column name for x-axis
        y : str or list
            Column name(s) for y-axis
        fig_name : str, optional
            Figure name/title
        save_path : str, optional
            Path to save the figure
        legend_location : str, optional
            Specific legend location ('upper right', 'lower left', etc.)
            If None, will automatically find best location
        legend_outside : bool
            If True, place legend outside the plot area
        ylim_mode : str
            Y-axis limit mode:
            - "auto": matplotlib default (automatic)
            - "data_extend": min(data) to max(data)*1.1
            - "percentage": 0 to 1 (for percentage data)
            - "zero_extend": 0 to max(data)*1.1
            - "custom": use ylim parameter
        ylim : tuple, optional
            Custom y-axis limits (min, max) when ylim_mode="custom"
        **kwargs
            Additional arguments passed to line plot

        Returns:
        --------
        tuple
            (figure, axes) objects
        """
        fig, ax = self._line_generator.create(
            data,
            x,
            y,
            title=fig_name,
            legend_preference=legend_location,
            legend_outside=legend_outside,
            ylim_mode=ylim_mode,
            ylim=ylim,
            **kwargs,
        )

        if save_path:
            self._save_figure(fig, save_path)

        return fig, ax

    def bar_plot(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        x: str,
        y: Union[str, List[str]],
        fig_name: Optional[str] = None,
        save_path: Optional[str] = None,
        legend_location: Optional[str] = None,
        legend_outside: bool = False,
        ylim_mode: str = "auto",
        ylim: Optional[tuple] = None,
        **kwargs,
    ) -> tuple:
        """
        Create a bar plot. Supports both single and grouped bar charts.

        Parameters:
        -----------
        data : DataFrame or dict
            Data to plot
        x : str
            Column name for categories
        y : str or list of str
            Column name(s) for values. If list, creates grouped bars
        fig_name : str, optional
            Figure name/title
        save_path : str, optional
            Path to save the figure
        legend_location : str, optional
            Specific legend location ('upper right', 'lower left', etc.)
            If None, will automatically find best location
        legend_outside : bool
            If True, place legend outside the plot area
        ylim_mode : str
            Y-axis limit mode:
            - "auto": matplotlib default (automatic)
            - "data_extend": min(data) to max(data)*1.1
            - "percentage": 0 to 1 (for percentage data)
            - "zero_extend": 0 to max(data)*1.1
            - "custom": use ylim parameter
        ylim : tuple, optional
            Custom y-axis limits (min, max) when ylim_mode="custom"
        **kwargs
            Additional arguments passed to bar plot

        Returns:
        --------
        tuple
            (figure, axes) objects
        """
        fig, ax = self._bar_generator.create(
            data,
            x,
            y,
            title=fig_name,
            legend_preference=legend_location,
            legend_outside=legend_outside,
            ylim_mode=ylim_mode,
            ylim=ylim,
            **kwargs,
        )

        if save_path:
            self._save_figure(fig, save_path)

        return fig, ax

    def scatter_plot(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        x: str,
        y: str,
        fig_name: Optional[str] = None,
        save_path: Optional[str] = None,
        **kwargs,
    ) -> tuple:
        """
        Create a scatter plot.

        Parameters:
        -----------
        data : DataFrame or dict
            Data to plot
        x : str
            Column name for x-axis
        y : str
            Column name for y-axis
        fig_name : str, optional
            Figure name/title
        save_path : str, optional
            Path to save the figure
        **kwargs
            Additional arguments passed to scatter plot

        Returns:
        --------
        tuple
            (figure, axes) objects
        """
        fig, ax = self._scatter_generator.create(data, x, y, title=fig_name, **kwargs)

        if save_path:
            self._save_figure(fig, save_path)

        return fig, ax

    def pie_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, List], pd.Series],
        fig_name: Optional[str] = None,
        save_path: Optional[str] = None,
        **kwargs,
    ) -> tuple:
        """
        Create a pie chart.

        Parameters:
        -----------
        data : DataFrame, dict, or Series
            Data to plot
        fig_name : str, optional
            Figure name/title
        save_path : str, optional
            Path to save the figure
        **kwargs
            Additional arguments passed to pie chart

        Returns:
        --------
        tuple
            (figure, axes) objects
        """
        fig, ax = self._pie_generator.create(data, title=fig_name, **kwargs)

        if save_path:
            self._save_figure(fig, save_path)

        return fig, ax

    def heatmap(
        self,
        data: Union[pd.DataFrame, np.ndarray],
        fig_name: Optional[str] = None,
        save_path: Optional[str] = None,
        **kwargs,
    ) -> tuple:
        """
        Create a heatmap.

        Parameters:
        -----------
        data : DataFrame or array
            Data to plot as heatmap
        fig_name : str, optional
            Figure name/title
        save_path : str, optional
            Path to save the figure
        **kwargs
            Additional arguments passed to heatmap

        Returns:
        --------
        tuple
            (figure, axes) objects
        """
        fig, ax = self._heatmap_generator.create(data, title=fig_name, **kwargs)

        if save_path:
            self._save_figure(fig, save_path)

        return fig, ax

    def _save_figure(self, fig: Figure, save_path: str) -> None:
        """Save figure to specified path with automatic format detection."""
        # Extract file extension
        if "." not in save_path:
            # If no extension provided, default to PDF
            save_path = save_path + ".pdf"

        # Determine format from extension
        extension = save_path.lower().split(".")[-1]

        # Set appropriate DPI based on format
        if extension in ["pdf", "eps", "svg"]:
            # Vector formats
            dpi = 300
        else:
            # Raster formats
            dpi = 300

        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", pad_inches=0.1)

    def get_template_info(self) -> Dict[str, Any]:
        """Get information about the current template."""
        return self.template.get_layout_info()

    def set_color_scheme(self, color_scheme: Union[str, ColorScheme]) -> None:
        """
        Change the color scheme.

        Parameters:
        -----------
        color_scheme : str or ColorScheme
            New color scheme to use
        """
        if isinstance(color_scheme, str):
            color_scheme = ColorScheme(color_scheme.lower())

        self.template.color_scheme = color_scheme
