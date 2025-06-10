import unittest
from unittest.mock import MagicMock, patch
from opcua import Client, ua
import logging
from EPHandler import EPlogin, SubHandler

class TestEPlogin(unittest.TestCase):

    @patch.object(Client, 'connect', return_value=None)  # Mock the connect method
    @patch.object(Client, 'disconnect', return_value=None)  # Mock the disconnect method
    @patch.object(Client, 'create_subscription', return_value=MagicMock())  # Mock create_subscription
    def test_connect_success(self, mock_connect, mock_disconnect, mock_create_subscription):
        # Mock successful connection
        endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
        ep_login = EPlogin(endpoint)

        # Test the connection
        connected = ep_login.connect()
        self.assertTrue(connected)

        # Ensure create_subscription was called
        mock_create_subscription.assert_called_once()


    @patch.object(Client, 'connect', return_value=None)
    @patch.object(Client, 'get_node', return_value=MagicMock())
    @patch.object(Client, 'create_subscription', return_value=MagicMock())
    def test_subscribe(self, mock_create_subscription, mock_get_node, mock_connect):
        # Test subscription logic
        endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
        ep_login = EPlogin(endpoint)
        ep_login.connect()

        # Define mock nodes and handler
        nodes = ["ns=2;s=Sensor1", "ns=2;s=Sensor2"]
        mock_handler = MagicMock()

        # Test the subscription
        ep_login.subscribe(nodes, mock_handler)

        # Ensure that get_node was called for each node
        mock_get_node.assert_any_call("ns=2;s=Sensor1")
        mock_get_node.assert_any_call("ns=2;s=Sensor2")

        # Ensure that subscription creation was called
        mock_create_subscription.assert_called_once()

    @patch.object(Client, 'connect', return_value=None)
    @patch.object(Client, 'get_node', return_value=MagicMock())
    
    def test_is_connected(self, mock_connect, mock_disconnect):
        # Mock a successful connection
        endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
        ep_login = EPlogin(endpoint)

        # Mock the client connection and session
        mock_client = MagicMock()
        mock_client.uaclient.session.active = True
        ep_login.client = mock_client

        self.assertTrue(ep_login.is_connected())

        # Mock a failed connection
        mock_client.uaclient.session.active = False
        self.assertFalse(ep_login.is_connected())

class TestSubHandler(unittest.TestCase):

    def test_datachange_notification(self):
        # Setup mock sensor pairs and sensors
        sensor_pairs = {
            "pair1": [{"start_name": "Sensor1", "end_name": "Sensor2"}]
        }
        sensors = {
            "Sensor1": {"current_state": 10, "previous_state": 5, "timestamp": None},
            "Sensor2": {"current_state": 20, "previous_state": 15, "timestamp": None},
        }

        # Mock the handle_time_difference function
        handle_time_difference = MagicMock()

        # Create a SubHandler instance
        handler = SubHandler(sensor_pairs, sensors, handle_time_difference)

        # Create a mock node and data change notification
        mock_node = MagicMock()
        mock_node.nodeid.to_string.return_value = "ns=2;s=Sensor1"
        mock_data = MagicMock()
        mock_data.monitored_item.Value.SourceTimestamp = 12345

        # Test the data change notification
        handler.datachange_notification(mock_node, 25, mock_data)

        # Check if the sensor state was updated
        self.assertEqual(sensors["Sensor1"]["previous_state"], 10)
        self.assertEqual(sensors["Sensor1"]["current_state"], 25)
        self.assertEqual(sensors["Sensor1"]["timestamp"], 12345)

        # Verify the handle_time_difference was called
        handle_time_difference.assert_called()

if __name__ == '__main__':
    unittest.main()
