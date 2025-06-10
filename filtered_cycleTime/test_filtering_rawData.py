import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from filtering_rawData import (  
    fetch_raw_data, calculate_limits, filter_real_time_data, write_filtered_data
)

class TestCycleTimeProcessing(unittest.TestCase):

    @patch('filtering_rawData.query_api.query_data_frame')  # Mock InfluxDB query
    def test_fetch_raw_data(self, mock_query):
        mock_query.return_value = pd.DataFrame({
            "_time": ["2025-03-10T12:00:00Z"],
            "_value": [100.0]
        })
        
        result = fetch_raw_data("test_pair", "2025-03-10T10:00:00Z", "2025-03-10T11:00:00Z", "test_line")

        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)

    def test_calculate_limits(self):
        data = pd.DataFrame({"_value": [10, 20, 30, 40, 50, 60, 70]})
        lower, upper = calculate_limits(data)
        
        self.assertGreater(upper, lower)
        self.assertGreaterEqual(lower, 0)

    def test_calculate_limits_no_data(self):
        lower, upper = calculate_limits(pd.DataFrame())
        self.assertIsNone(lower)
        self.assertIsNone(upper)

    def test_filter_real_time_data(self):
        data = pd.DataFrame({"_value": [20, 30, 40, 50, 60]})
        filtered = filter_real_time_data(data, 25, 55)

        self.assertFalse(filtered.empty)
        self.assertEqual(len(filtered), 3)  # Only values between 25 and 55

    def test_filter_real_time_data_no_data(self):
        filtered = filter_real_time_data(pd.DataFrame(), 10, 50)
        self.assertTrue(filtered.empty)

    @patch('filtering_rawData.write_api.write')  # Mock write API
    def test_write_filtered_data(self, mock_write):
        data = pd.DataFrame({
            "_time": ["2025-03-10T12:00:00Z"],
            "_value": [100.0]
        })
        write_filtered_data(data, "test_pair", "test_line")

        mock_write.assert_called_once()

if __name__ == "__main__":
    unittest.main()
