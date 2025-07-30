from typing import Any

import pandas as pd

from .find_RP.poncelet import poncelet_method
from .find_RP.kmedoids import kmedoids_method
from .find_RP.random import random_method
from .plot import show_curves, show_DC, show_RP
from .export import save_RP


class TemporalData:
    def __init__(self, data: pd.DataFrame) -> None:
        """
        Initialize a TemporalData object.

        Args:
            data (pd.DataFrame): The data containing temporal curves.

        Raises:
            ValueError: If input data is not a DataFrame from pandas or if the index of the DataFrame is not a DatetimeIndex.
        """
        # Check if data is a pandas DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a DataFrame from pandas.")

        # Check if the index of the DataFrame is a DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Index of the DataFrame must be a DatetimeIndex.")

        # Assign the data to the class attribute
        self.data = data
        self.RP = None

    @property
    def curve_set(self) -> pd.Index:
        """Get the set of curves (column names) in the data.

        Returns:
            list: A list of curve names.
        """
        return self.data.columns

    @property
    def time_horizon(self) -> pd.DatetimeIndex:
        """Get the time horizon (index) of the data.

        Returns:
            pd.DatetimeIndex: The time horizon of the data.

        """
        return self.data.index

    def calculate_RP(
        self,
        method: str,
        N_RP: int,
        RP_length: int,
        N_bins: int = 15,
        solver: Any = None,
    ):
        """Calculate representative periods (RPs) using the specified method.

        Could be improved using protocol or ABC

        Args:
            method (str): The method to use for RP calculation ("poncelet", "kmedoids", or "random").
            N_RP (int): The number of representative periods to calculate.
            RP_length (int): The length of each representative period.
            N_bins (int, optional): The number of bins for duration curve discretization. Defaults to 15.
            solver: An optional solver object for optimization (required for "poncelet" method).

        Raises:
            ValueError: If an invalid method is provided.

        Returns:
            None
        """
        if method == "poncelet":
            self.RP = poncelet_method(
                self.data, self.curve_set, N_RP, RP_length, N_bins, solver
            )
        elif method == "kmedoids":
            self.RP = kmedoids_method(self.data, N_RP, RP_length)
        elif method == "random":
            self.RP = random_method(self.data, N_RP, RP_length)
        else:
            raise ValueError(
                "Invalid method. Supported methods: 'poncelet', 'kmedoids', 'random'"
            )

    def plot_curves(self):
        """Plot the original curves.

        Returns:
            go.Figure: A Plotly figure displaying the original curves.
        """
        return show_curves(self.data, self.curve_set)

    def plot_RP(self):
        """Plot the representative periods (RPs).

        Returns:
            go.Figure: A Plotly figure displaying the RPs.
        """
        check_is_RP(self)
        return show_RP(self.data, self.curve_set, self.RP)

    def plot_DC(self):
        """Plot the duration curves (DCs) of the original data and combined RPs.

        Returns:
            go.Figure: A Plotly figure displaying the DCs.
        """
        check_is_RP(self)
        return show_DC(self.data, self.curve_set, self.RP)

    def export(self, folder_path: str = "./", sep: str = ","):
        """
        Export representative periods (RPs) and their weights to CSV files.

        Args:
            folder_path (str, optional): The path to the folder where the files will be saved. Defaults to './'.
            sep (str, optional): The separator used in the CSV files. Defaults to ','.

        Raises:
            ValueError: If RPs have not been calculated for the TemporalData object.

        Returns:
            None
        """
        # Check if RPs have been calculated
        check_is_RP(self)

        # Save RPs and their weights to CSV files in the specified folder
        save_RP(folder_path, self.RP, sep)


def check_is_RP(temporal_data: TemporalData):
    """Check if RPs have been calculated for the TemporalData object.

    Args:
        temporal_data (TemporalData): A TemporalData object.

    Raises:
        ValueError: If RPs have not been calculated.
    """
    if temporal_data.RP is None:
        raise ValueError(
            "Representative periods (RPs) have not been calculated. Use calculate_RP method first."
        )
