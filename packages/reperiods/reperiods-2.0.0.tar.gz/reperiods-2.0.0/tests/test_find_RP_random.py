import pandas as pd
import numpy as np
from reperiods import TemporalData, RepresentativePeriods


def test_random_method():
    length = 168
    data = pd.read_csv(
        "reperiods/datasets/example_dataset.csv", sep=";", header=3, usecols=[1, 2]
    ).iloc[:length]
    # Rename columns for clarity.
    data.columns = ["Wind", "PV"]
    # Generate a time index starting from "2015-01-01" with hourly frequency for 8760 periods.
    data.index = pd.date_range(start="2015-01-01", freq="h", periods=length)

    N_RP = 2
    RP_length = 12

    temporal_data = TemporalData(data)
    temporal_data.calculate_RP(
        method="kmedoids", N_RP=N_RP, RP_length=RP_length, N_bins=15
    )

    # Check that each RepresentativePeriods object has the correct data and weight attributes
    for rp in temporal_data.RP:
        assert isinstance(rp, RepresentativePeriods)
        assert isinstance(rp.data, pd.DataFrame)
        assert rp.data.shape[0] == RP_length
        assert rp.data.shape[1] == 2
        assert isinstance(rp.weight, float)

    # Check that the sum of the weights is approximately equal to 1 (allowing for some error due to floating point precision)
    assert np.isclose(sum([rp.weight for rp in temporal_data.RP]), 1.0)
