import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .representative_periods import RepresentativePeriods
from .utils import duration_function


def show_curves(data: pd.DataFrame, curve_set: pd.Index) -> go.Figure:
    """Visualize curves in a TemporalData object.

    Args:
        data (DataFrame): A DataFrame containing the data where RP will be found
        curve_set (Index): A set of curve linked to the data

    Returns:
        go.Figure: A Plotly figure showing the curves.
    """
    # Create an empty Plotly figure
    fig = go.Figure()

    # Loop through each curve in the temporal_data object
    for curve in curve_set:
        # Add a scatter plot trace for the curve
        fig.add_trace(
            go.Scatter(
                x=data.index,  # X-axis data (time horizon)
                y=data[curve],  # Y-axis data (curve values)
                name=curve,  # Name for the curve in the legend
            )
        )

    return fig


def show_RP(
    data: pd.DataFrame, curve_set: pd.Index, RPs: list[RepresentativePeriods]
) -> go.Figure:
    """Visualize representative periods (RPs) on a plot of curves.

    Args:
        data (DataFrame): A DataFrame containing the data where RP will be found
        curve_set (Index): A set of curve linked to the data
        RPs (list[RepresentativePeriods]): list of representative periods attributed to the data

    Returns:
        go.Figure: A Plotly figure with RPs highlighted in green.
    """
    # Create a figure by plotting the curves
    fig = show_curves(data, curve_set)

    # Add vertical rectangles for each RP
    for RP in RPs:
        # Add a vertical rectangle (shaded region) to highlight the RP's time range
        fig.add_vrect(
            x0=RP.data.index.min(),
            x1=RP.data.index.max(),
            annotation_text=f"weight: {RP.weight * 100:.2f}%",
            annotation_position="top left",
            fillcolor="green",
            opacity=0.25,
            line_width=0,
        )

    return fig


def show_DC(
    data: pd.DataFrame, curve_set: pd.Index, RPs: list[RepresentativePeriods]
) -> go.Figure:
    """Visualize duration curves (DC) of the original data and the combined RPs.

    Args:
        data (DataFrame): A DataFrame containing the data where RP will be found
        curve_set (Index): A set of curve linked to the data
        RPs (list[RepresentativePeriods]): list of representative periods attributed to the data

    Returns:
        go.Figure: A Plotly figure displaying duration curves.
    """
    # Define a set of colors for the curves
    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    # Create an empty Plotly figure
    fig = go.Figure()

    # Generate a range of Y values (percentiles)
    Y = np.linspace(0, 1, 100)

    # Loop through each curve in the temporal_data object
    for i, curve in enumerate(curve_set):
        # Add the original duration curve as a solid line
        fig.add_trace(
            go.Scatter(
                x=np.vectorize(duration_function(data[curve]))(Y),
                y=Y,
                name=f"Original DC {curve}",
                line_color=colors[i % 10],
            )
        )

        # Add the combined duration curve (weighted sum of RPs) as a dashed line
        fig.add_trace(
            go.Scatter(
                x=sum(
                    np.vectorize(duration_function(RP.data[curve]))(Y) * RP.weight
                    for RP in RPs
                ),
                y=Y,
                name=f"Combined DC {curve}",
                line_color=colors[i % 10],
                line_dash="dash",
            )
        )

    return fig
