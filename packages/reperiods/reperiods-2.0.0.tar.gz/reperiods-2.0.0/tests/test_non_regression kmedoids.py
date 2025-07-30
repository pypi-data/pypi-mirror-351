import pandas as pd
import reperiods as rp

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

temporal_data = rp.TemporalData(data)
temporal_data.calculate_RP(method="kmedoids", N_RP=N_RP, RP_length=RP_length, N_bins=15)

weight_RP_00 = 0.42857142857142855
weight_RP_01 = 0.5714285714285714

data_RP_00 = pd.DataFrame(
    [
        [0.3567984570877531, 0.2665627435697584],
        [0.3895853423336547, 0.2665627435697584],
        [0.390549662487946, 0.2291504286827747],
        [0.3857280617164899, 0.1527669524551831],
        [0.3857280617164899, 0.0514419329696024],
        [0.3876567020250723, 0.0007794232268121],
        [0.4156219864995178, 0.0],
        [0.4329797492767598, 0.0],
        [0.4021215043394407, 0.0],
        [0.3828351012536162, 0.0],
        [0.3635486981677917, 0.0],
        [0.3394406943105111, 0.0],
    ],
    columns=["Wind", "PV"],
    index=pd.date_range("2015-01-06 12:00", periods=12, freq="h"),
)

data_RP_01 = pd.DataFrame(
    [
        [0.2912246865959498, 0.0],
        [0.2381870781099325, 0.0],
        [0.2150433944069431, 0.0],
        [0.18900675024108, 0.0],
        [0.1600771456123433, 0.0],
        [0.1234329797492767, 0.0],
        [0.1253616200578592, 0.0],
        [0.1465766634522661, 0.0],
        [0.2169720347155255, 0.0],
        [0.2044358727097396, 0.0646921278254092],
        [0.1764705882352941, 0.1761496492595479],
        [0.1658630665380906, 0.2876071706936867],
    ],
    columns=["Wind", "PV"],
    index=pd.date_range("2015-01-07 00:00", periods=12, freq="h"),
)


def test_non_regression_poncelet():
    assert temporal_data.RP[0].data.equals(data_RP_00)
    assert temporal_data.RP[1].data.equals(data_RP_01)
    assert temporal_data.RP[0].weight == weight_RP_00
    assert temporal_data.RP[1].weight == weight_RP_01
