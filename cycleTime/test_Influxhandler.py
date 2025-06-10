import unittest
from unittest.mock import patch, MagicMock
from Influxhandler import PostOPCUAdata  # Replace with the actual import path

class TestPostOPCUAdata(unittest.TestCase):

    @patch('Influxhandler.write_api.write')  # Mock the InfluxDB write method
    def test_post_opcua_data_success(self, mock_write):
        # Call function with test data
        result = PostOPCUAdata("test_name", 123.45)

        # Ensure the write function was called once
        mock_write.assert_called_once()

        # Check the function return value
        self.assertEqual(result, ("test_name", 123.45))

    @patch('Influxhandler.write_api.write', side_effect=Exception("InfluxDB Error"))
    def test_post_opcua_data_failure(self, mock_write):
        # Call function with test data, expecting it to handle the exception
        result = PostOPCUAdata("test_name", 123.45)

        # Ensure the write function was called once
        mock_write.assert_called_once()

        # Function should return (None, None) on error
        self.assertEqual(result, (None, None))

if __name__ == "__main__":
    unittest.main()
