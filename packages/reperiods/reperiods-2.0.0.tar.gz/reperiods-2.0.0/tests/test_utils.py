import pandas as pd
from reperiods.utils import duration_function


def test_duration_function():
    # Create a sample pandas Series for testing
    series = pd.Series(range(10))

    # Test with default parameters
    duration_func = duration_function(series)
    assert duration_func(5) == 0.5  # half of the series is above 5

    # Test with production_normalized=True
    duration_func = duration_function(series, production_normalized=True)
    assert duration_func(0.5) == 0.5  # half of the normalized series is above 0.5

    # Test with time_normalized=False
    duration_func = duration_function(series, time_normalized=False)
    assert duration_func(5) == 5  # 5 elements of the series are above 5


# Run the test
test_duration_function()
