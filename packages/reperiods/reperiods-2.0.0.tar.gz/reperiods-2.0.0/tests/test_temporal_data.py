import unittest
import numpy as np
import pandas as pd
from reperiods import TemporalData
from reperiods.temporal_data import check_is_RP


class TestTemporalData(unittest.TestCase):
    def setUp(self):
        # Create a time index with 336 entries, one for each hour in 14 days
        index = pd.date_range(start="1/1/2022", periods=336, freq="h")

        # Create a sinusoidal curve with a period of 24 hours (to represent daily variation)
        data = {"curve1": np.sin(2 * np.pi * (np.arange(336) / 24))}

        # Create a DataFrame from the data and set the time index
        self.data = pd.DataFrame(data, index=index)

        # Initialize a TemporalData object with the DataFrame
        self.td = TemporalData(self.data)

    def test_init(self):
        self.assertIsInstance(self.td.data, pd.DataFrame)
        self.assertIsInstance(self.td.data.index, pd.DatetimeIndex)

    def test_curve_set(self):
        self.assertEqual(self.td.curve_set.tolist(), ["curve1"])

    def test_time_horizon(self):
        self.assertEqual(self.td.time_horizon.tolist(), self.data.index.tolist())

    def test_check_is_RP(self):
        with self.assertRaises(ValueError):
            check_is_RP(self.td)

    def test_calculate_RP(self):
        # This test depends on the implementation of the methods: poncelet_method, kmedoids_method, random_method
        # For now, we'll just check if the method doesn't raise an error
        self.td.calculate_RP("poncelet", 2, 5)
        self.assertIsNotNone(self.td.RP)


if __name__ == "__main__":
    unittest.main()
