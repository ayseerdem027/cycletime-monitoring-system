import unittest
from unittest.mock import patch, MagicMock
import datetime
import time_difference_calc as TDC

# Assuming your module is named `your_module` and it contains `handle_time_difference`
# from your_module import handle_time_difference

class TestHandleTimeDifference(unittest.TestCase):

    @patch('Influxhandler.PostOPCUAdata')  # Mock the Influxhandler.PostOPCUAdata method
    @patch('logging.info')  # Mock logging
    def test_handle_time_difference(self, mock_logging, mock_post_opcua_data):
        # Prepare mock data for the sensors
        pair = {
            "start_name": "sensor_start",
            "end_name": "sensor_end",
            "start_default": "default_start",
            "end_default": "default_end",
            "station": "station_1"
        }

        sensors = {
            "sensor_start": {
                "previous_state": "default_start",
                "current_state": "active",  # The state changes to active, indicating an event start
                "timestamp": datetime.datetime(2025, 3, 10, 12, 0, 0),
                "event_processed": False,
                "movement_start_timestamp": None
            },
            "sensor_end": {
                "previous_state": "active",
                "current_state": "default_end",  # The state resets to the default, indicating event end
                "timestamp": datetime.datetime(2025, 3, 10, 12, 0, 5),
            }
        }

        # Call the function to test
        TDC.handle_time_difference(pair, sensors)

        # Check if logging was called (log should contain time difference)
        mock_logging.assert_called_with("Time difference (ms): 5000.0, Station: station_1")

        # Ensure that the InfluxDB call was made with the correct parameters
        mock_post_opcua_data.assert_called_once_with(
            "Zeitdifferenz", 5000.0, {"pair_name": "station_1"}, {"assembly_line": None}
        )

        # Check if the sensor states were updated correctly
        self.assertTrue(sensors["sensor_start"]["event_processed"])
        self.assertIsNone(sensors["sensor_start"]["movement_start_timestamp"])

    def test_handle_time_difference_invalid_time(self):
        # Test with invalid time difference (e.g., a time difference > 600000 ms)
        pair = {
            "start_name": "sensor_start",
            "end_name": "sensor_end",
            "start_default": "default_start",
            "end_default": "default_end",
            "station": "station_1"
        }

        sensors = {
            "sensor_start": {
                "previous_state": "default_start",
                "current_state": "active",
                "timestamp": datetime.datetime(2025, 3, 10, 12, 0, 0),
                "event_processed": False,
                "movement_start_timestamp": None
            },
            "sensor_end": {
                "previous_state": "active",
                "current_state": "default_end",
                "timestamp": datetime.datetime(2025, 3, 10, 12, 15, 0),  # Time difference too large
            }
        }

        with patch('Influxhandler.PostOPCUAdata') as mock_post_opcua_data, patch('logging.info') as mock_logging:
            TDC.handle_time_difference(pair, sensors)

            # Ensure no InfluxDB call was made for invalid time difference
            mock_post_opcua_data.assert_not_called()

            # Ensure the state of the sensors is still unprocessed and no event was triggered
            self.assertFalse(sensors["sensor_start"]["event_processed"])
            self.assertIsNone(sensors["sensor_start"]["movement_start_timestamp"])

if __name__ == '__main__':
    unittest.main()
