import pandas as pd


def load_renewable(length: int = 336) -> pd.DataFrame:
    """Load renewable energy data from a CSV file.

    Args:
        length (int, optional): The number of data points (hours) to load. Defaults to 336 (2 weeks).

    Returns:
        pandas.DataFrame: A DataFrame containing renewable hourly capacity factor data with columns 'Wind' and 'PV'.
    """
    # Load data from a CSV file located in the "./periods/datasets" directory.
    data = pd.read_csv(
        "https://raw.githubusercontent.com/RobinsonBeaucour/reperiods-beta/beta/reperiods/datasets/example_dataset.csv",
        sep=";",
        header=3,
        usecols=[1, 2],
    )

    # Rename columns for clarity.
    data.columns = ["Wind", "PV"]

    # Generate a time index starting from "2015-01-01" with hourly frequency for 8760 periods.
    data.index = pd.date_range(start="2015-01-01", freq="h", periods=8760)

    # Return the first 'length' data points (default is 336).
    return data.iloc[:length]
