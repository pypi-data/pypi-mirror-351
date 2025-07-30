#!/usr/bin/env python3
"""
Demo script showcasing intelligent legend positioning.
"""

import pandas as pd
import numpy as np
from src.draw_paper import AcademicPlotter


def create_crowded_data():
    """Create data that would cause legend overlap issues."""
    np.random.seed(42)

    # Data that fills most of the plot area
    x = np.linspace(0, 10, 100)

    # Multiple series with data in different regions
    data = pd.DataFrame(
        {
            "x": x,
            "upper_right_heavy": 2
            + 0.5 * x
            + 0.2 * np.sin(x)
            + 0.1 * np.random.randn(100),
            "upper_left_heavy": 8
            - 0.3 * x
            + 0.3 * np.cos(x)
            + 0.1 * np.random.randn(100),
            "lower_center": 3
            + 0.1 * x
            + 0.5 * np.sin(2 * x)
            + 0.1 * np.random.randn(100),
            "everywhere": 5
            + 0.8 * np.sin(x)
            + 0.5 * np.cos(2 * x)
            + 0.1 * np.random.randn(100),
        }
    )

    return data


def create_bar_data():
    """Create bar chart data for legend positioning demo."""
    return pd.DataFrame(
        {
            "categories": [
                "Category A",
                "Category B",
                "Category C",
                "Category D",
                "Category E",
            ],
            "Method 1": [85, 92, 78, 88, 90],
            "Method 2": [80, 88, 82, 85, 87],
            "Method 3": [88, 85, 79, 90, 89],
            "Baseline": [75, 80, 72, 78, 82],
        }
    )


def demo_intelligent_legend():
    """Demonstrate intelligent legend positioning."""
    print("Creating intelligent legend positioning demos...")

    # Create sample data
    line_data = create_crowded_data()
    bar_data = create_bar_data()

    plotter = AcademicPlotter(layout="single", size="medium", color_scheme="nature")

    # Demo 1: Automatic legend positioning for line plot
    print("1. Automatic legend positioning (line plot)...")
    fig, ax = plotter.line_plot(
        data=line_data,
        x="x",
        y=["upper_right_heavy", "upper_left_heavy", "lower_center"],
        fig_name="Automatic Legend Positioning",
        xlabel="X Values",
        ylabel="Y Values",
        legend=True,
        save_path="figs/legend_auto_line.pdf",
    )
    print("   ✓ Saved as legend_auto_line.pdf")

    # Demo 2: Force legend to upper right (might overlap)
    print("2. Forced upper right positioning...")
    fig, ax = plotter.line_plot(
        data=line_data,
        x="x",
        y=["upper_right_heavy", "upper_left_heavy", "lower_center"],
        fig_name="Forced Upper Right Legend",
        xlabel="X Values",
        ylabel="Y Values",
        legend=True,
        legend_location="upper right",
        save_path="figs/legend_forced_line.pdf",
    )
    print("   ✓ Saved as legend_forced_line.pdf")

    # Demo 3: Legend outside plot area
    print("3. Legend outside plot area...")
    fig, ax = plotter.line_plot(
        data=line_data,
        x="x",
        y=["upper_right_heavy", "upper_left_heavy", "lower_center", "everywhere"],
        fig_name="Outside Legend",
        xlabel="X Values",
        ylabel="Y Values",
        legend=True,
        legend_outside=True,
        save_path="figs/legend_outside_line.pdf",
    )
    print("   ✓ Saved as legend_outside_line.pdf")

    # Demo 4: Grouped bar chart with automatic legend
    print("4. Automatic legend for grouped bars...")
    fig, ax = plotter.bar_plot(
        data=bar_data,
        x="categories",
        y=["Method 1", "Method 2", "Method 3", "Baseline"],
        fig_name="Grouped Bar Chart - Auto Legend",
        xlabel="Categories",
        ylabel="Performance (%)",
        legend=True,
        save_path="figs/legend_auto_bar.pdf",
    )
    print("   ✓ Saved as legend_auto_bar.pdf")

    # Demo 5: Grouped bar chart with outside legend
    print("5. Outside legend for grouped bars...")
    fig, ax = plotter.bar_plot(
        data=bar_data,
        x="categories",
        y=["Method 1", "Method 2", "Method 3", "Baseline"],
        fig_name="Grouped Bar Chart - Outside Legend",
        xlabel="Categories",
        ylabel="Performance (%)",
        legend=True,
        legend_outside=True,
        save_path="figs/legend_outside_bar.pdf",
    )
    print("   ✓ Saved as legend_outside_bar.pdf")

    # Demo 6: Compare different positioning strategies
    print("6. Comparison of positioning strategies...")

    # Create a 2x2 subplot comparison using double column layout
    plotter_double = AcademicPlotter(
        layout="double", size="large", color_scheme="science"
    )

    # We'll create individual plots since the current API doesn't support subplots
    # This demonstrates the flexibility of the system

    strategies = [
        ("Auto Position", None, False),
        ("Upper Right", "upper right", False),
        ("Lower Left", "lower left", False),
        ("Outside", None, True),
    ]

    for i, (name, location, outside) in enumerate(strategies):
        fig, ax = plotter.line_plot(
            data=line_data.head(50),  # Use less data for clarity
            x="x",
            y=["upper_right_heavy", "upper_left_heavy", "lower_center"],
            fig_name=f"Strategy: {name}",
            xlabel="X Values",
            ylabel="Y Values",
            legend=True,
            legend_location=location,
            legend_outside=outside,
            save_path=f"figs/legend_strategy_{i+1}_{name.lower().replace(' ', '_')}.pdf",
        )
        print(f"   ✓ Saved strategy {i+1}: {name}")


def demo_legend_best_practices():
    """Show best practices for legend usage in academic papers."""
    print("\nDemonstrating legend best practices...")

    # Create data for different scenarios
    simple_data = pd.DataFrame(
        {
            "x": range(1, 11),
            "Proposed Method": [85, 87, 89, 91, 93, 94, 95, 96, 97, 98],
            "Baseline": [75, 77, 78, 80, 82, 83, 84, 85, 86, 87],
            "State-of-the-Art": [80, 82, 84, 86, 88, 90, 91, 92, 93, 94],
        }
    )

    plotter = AcademicPlotter(layout="single", size="medium", color_scheme="academic")

    # Best Practice 1: Clear, descriptive legend labels
    print("1. Clear, descriptive labels...")
    fig, ax = plotter.line_plot(
        data=simple_data,
        x="x",
        y=["Proposed Method", "Baseline", "State-of-the-Art"],
        fig_name="Performance Comparison",
        xlabel="Iteration",
        ylabel="Accuracy (%)",
        legend=True,
        save_path="figs/legend_best_practice_labels.pdf",
    )
    print("   ✓ Good: Descriptive method names")

    # Best Practice 2: Outside legend for many items
    many_methods_data = pd.DataFrame(
        {
            "x": range(1, 11),
            "Method A": simple_data["Proposed Method"] + np.random.randn(10) * 2,
            "Method B": simple_data["Baseline"] + np.random.randn(10) * 2,
            "Method C": simple_data["State-of-the-Art"] + np.random.randn(10) * 2,
            "Method D": simple_data["Proposed Method"] - 5 + np.random.randn(10) * 2,
            "Method E": simple_data["Baseline"] + 3 + np.random.randn(10) * 2,
            "Method F": simple_data["State-of-the-Art"] - 2 + np.random.randn(10) * 2,
        }
    )

    print("2. Many methods - outside legend...")
    fig, ax = plotter.line_plot(
        data=many_methods_data,
        x="x",
        y=["Method A", "Method B", "Method C", "Method D", "Method E", "Method F"],
        fig_name="Multiple Methods Comparison",
        xlabel="Iteration",
        ylabel="Performance",
        legend=True,
        legend_outside=True,
        save_path="figs/legend_best_practice_many.pdf",
    )
    print("   ✓ Good: Outside legend for many items")


if __name__ == "__main__":
    print("Legend Positioning Demo")
    print("=" * 40)

    demo_intelligent_legend()
    demo_legend_best_practices()

    print("\n" + "=" * 40)
    print("All legend demos completed!")
    print("Check the figs/ directory for generated PDFs.")
    print("\nKey features demonstrated:")
    print("• Automatic legend positioning based on content density")
    print("• Manual legend location override")
    print("• Outside legend placement")
    print("• Best practices for academic papers")
