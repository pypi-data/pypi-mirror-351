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
temporal_data.calculate_RP(method="poncelet", N_RP=N_RP, RP_length=RP_length, N_bins=15)

weight_RP_00 = 0.45238095
weight_RP_01 = 0.54761905

data_RP_00 = pd.DataFrame(
    [
        [0.2034715525554484, 0.0],
        [0.1668273866923818, 0.0],
        [0.133076181292189, 0.0],
        [0.1051108968177435, 0.0],
        [0.0675024108003857, 0.0],
        [0.0597878495660559, 0.0],
        [0.0781099324975892, 0.0],
        [0.1022179363548698, 0.0],
        [0.1465766634522661, 0.0007794232268121],
        [0.1668273866923818, 0.0771628994544037],
        [0.18900675024108, 0.2151208106001559],
        [0.2150433944069431, 0.3156664068589244],
    ],
    columns=["Wind", "PV"],
    index=pd.date_range("2015-01-01 00:00", periods=12, freq="h"),
)

data_RP_01 = pd.DataFrame(
    [
        [0.5544840887174542, 0.2431800467653936],
        [0.5361620057859209, 0.2517537022603273],
        [0.5226615236258437, 0.2174590802805923],
        [0.5188042430086789, 0.147310989867498],
        [0.5043394406943105, 0.0498830865159781],
        [0.5197685631629702, 0.0015588464536243],
        [0.4416586306653809, 0.0],
        [0.3837994214079074, 0.0],
        [0.3471552555448409, 0.0],
        [0.2892960462873674, 0.0],
        [0.2700096432015429, 0.0],
        [0.2092574734811957, 0.0],
    ],
    columns=["Wind", "PV"],
    index=pd.date_range("2015-01-04 12:00", periods=12, freq="h"),
)


def test_non_regression_poncelet():
    assert temporal_data.RP[0].data.equals(data_RP_00)
    assert temporal_data.RP[1].data.equals(data_RP_01)
    assert temporal_data.RP[0].weight == weight_RP_00
    assert temporal_data.RP[1].weight == weight_RP_01
