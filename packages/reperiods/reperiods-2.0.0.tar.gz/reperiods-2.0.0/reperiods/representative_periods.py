import pandas as pd


class RepresentativePeriods:
    """Represents a single representative period with associated data and weight.

    Args:
        data (pd.DataFrame): The data associated with the representative period.
        weight (float): The weight of the representative period (between 0 and 1).

    Raises:
        ValueError: If input data is not a DataFrame from pandas, if the index of the DataFrame is not a DatetimeIndex,
            or if the weight is not a float between 0 and 1.
    """

    def __init__(self, data: pd.DataFrame, weight: float):
        """
        Initialize a RepresentativePeriods object.

        Args:
            data (pd.DataFrame): The data associated with the representative period.
            weight (float): The weight of the representative period (between 0 and 1).

        Raises:
            ValueError: If input data is not a DataFrame from pandas, if the index of the DataFrame is not a DatetimeIndex,
                or if the weight is not a float between 0 and 1.
        """
        # Check if data is a pandas DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a DataFrame from pandas.")

        # Check if the index of the DataFrame is a DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Index of the DataFrame must be a DatetimeIndex.")

        # Check if weight is a float between 0 and 1
        if not isinstance(weight, float) or not 0 <= weight <= 1:
            raise ValueError("Weight must be a float between 0 and 1")

        # Assign the data and weight to class attributes
        self.data = data
        self.weight = weight
