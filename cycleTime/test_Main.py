import unittest
from unittest.mock import patch, MagicMock
import json
import os
from Main import main  # Ensure Main is the correct import path for your module
import time

class TestMain(unittest.TestCase):

    @patch('Main.EPManager')  # Mock the EPManager used in the Main module
    @patch('Main.time.sleep', side_effect=KeyboardInterrupt)  # Mock time.sleep to raise KeyboardInterrupt immediately
    @patch('Main.os.getenv')
    @patch('Main.json.loads')
    def test_main(self, mock_json_loads, mock_getenv, mock_sleep, MockEPManager):
        # Mock environment variables as if they were loaded from .env
        mock_getenv.side_effect = lambda key: '{"ep1": "endpoint1"}' if key == "ENDPOINTS" else \
                                              '{"ep1": ["pair1"]}' if key == "ENDPOINT_LINES" else \
                                              '{"pair1": "namespace1"}' if key == "NAMESPACES" else None
        
        # Mock json.loads to return the proper structure
        mock_json_loads.side_effect = lambda x: json.loads(x)

        # Create a mock instance of EPManager
        mock_manager_instance = MockEPManager.return_value

        # Run the main function and expect it to raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            main()

        # Check if EPManager was initialized correctly
        MockEPManager.assert_called_once()  # This ensures that EPManager is instantiated once

        # Check if connect_all and disconnect_all were called once
        mock_manager_instance.connect_all.assert_called_once()
        mock_manager_instance.disconnect_all.assert_called_once()

if __name__ == "__main__":
    unittest.main()
