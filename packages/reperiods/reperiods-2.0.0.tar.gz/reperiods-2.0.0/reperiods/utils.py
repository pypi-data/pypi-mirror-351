import pandas as pd


def duration_function(
    series: pd.Series, production_normalized=False, time_normalized=True
):
    """
    Returns a function that calculates the duration of a time series above a given threshold.
    This function considered that all point represent the same duration.

    Args:
        series (pd.Series): A pandas series representing a time series like load or production.
        production_normalized (bool, optional): Whether to normalize the series to be between 0 and 1. Defaults to True.
        time_normalized (bool, optional): Whether to return a function that normalizes the duration as a proportion of the total series length. Defaults to True.

    Returns:
        function: A lambda function that takes a threshold value and returns the duration of the series above that threshold, either as a proportion of the total series length or as a raw count, depending on the value of `time_normalized`.

    Example:
        duration_func = duration_function(series)
        duration_above_5 = duration_func(5)  # calculates the duration of the series above 5
    """
    series_to_use = series.copy()  # create a copy of the input series to modify
    if production_normalized:
        series_to_use = (series_to_use - series_to_use.min()) / (
            series_to_use.max() - series_to_use.min()
        )  # normalize the series to be between 0 and 1
    if time_normalized:
        return (
            lambda x: (series_to_use >= x).sum() / series_to_use.shape[0]
        )  # return a function that calculates the proportion of the series above a threshold value
    else:
        return (
            lambda x: (series_to_use >= x).sum()
        )  # return a function that calculates the raw count of the series above a threshold value
