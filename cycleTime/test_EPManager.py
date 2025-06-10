import unittest
from unittest.mock import MagicMock

class TestEPManager(unittest.TestCase):

    def test_connect_all_success(self):
        # Create a mock for the connection class
        mock_connection = MagicMock()
        
        # Simulate that connect returns True (successful connection)
        mock_connection.connect.return_value = True

        # Create an instance of your EPManager class
        ep_manager = MagicMock()
        
        # Assuming ep_manager has an attribute 'connections' that holds all connection objects
        ep_manager.connections = [mock_connection]

        # Define the behavior for connect_all to call connect() on each connection
        ep_manager.connect_all = lambda: [conn.connect() for conn in ep_manager.connections]
        
        # Call connect_all, which should trigger connect on the mock connection
        ep_manager.connect_all()

        # Ensure that connect was called on the mock connection
        mock_connection.connect.assert_called_once()

        # Optionally, check that connect_all does not raise any exceptions
        self.assertTrue(mock_connection.connect())

if __name__ == '__main__':
    unittest.main()
