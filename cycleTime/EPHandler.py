import logging
import time
from opcua import Client, ua

class EPlogin:
    """Handles OPC UA connection and subscriptions for a single endpoint."""
    
    MAX_RETRIES = 10
    INITIAL_RETRY_DELAY = 1  # Initial delay in seconds
    MAX_RETRY_DELAY = 60  # Maximum delay in seconds

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.client = None
        self.subscription = None
        self.subscribed_nodes = {}

    def connect(self):
        """Tries to establish a connection with optional basic authentication and exponential backoff."""
        retries = 0
        delay = self.INITIAL_RETRY_DELAY

        while retries < self.MAX_RETRIES:
            try:
                print(f"Attempting to connect to {self.endpoint}, attempt {retries+1}")
                self.client = Client(self.endpoint)
                self.client.connect()
                logging.debug(f"Connected to {self.endpoint}")
                return True
            except (ua.UaStatusCodeError, ConnectionError, TimeoutError, OSError) as e:
                retries += 1
                logging.error(f"Connection failed ({retries}/{self.MAX_RETRIES}) to {self.endpoint}: {e}")
                
                if retries >= self.MAX_RETRIES:
                    return False

                print(f"Sleeping for {delay} seconds before retry")
                time.sleep(delay)
                delay = min(delay * 2, self.MAX_RETRY_DELAY)

    def disconnect(self):
        """Closes the connection and cleans up resources."""
        if self.client:
            try:
                if self.subscription:
                    self.subscription.delete()
                self.client.disconnect()
                self.client.close_session()
                logging.debug(f"Disconnected from {self.endpoint}")
            except Exception as e:
                logging.error(f"Error disconnecting from {self.endpoint}: {e}")
            finally:
                self.client = None

    def subscribe(self, nodes, handler):
        """Subscribes to given nodes with a specified handler."""
        if not self.client:
            logging.error("Cannot subscribe - no active connection.")
            return

        try:
            # If a previous subscription exists, delete it before re-subscribing
            if self.subscription:
                try:
                    self.subscription.delete()
                    self.subscribed_nodes.clear()
                except Exception as e:
                    logging.error(f"Error deleting previous subscription on {self.endpoint}: {e}")

            self.subscription = self.client.create_subscription(1000, handler)
            for node_str in nodes:
                try:
                    node = self.client.get_node(node_str)
                    handle = self.subscription.subscribe_data_change(node)
                    self.subscribed_nodes[node_str] = handle
                except Exception as e:
                    logging.error(f"Subscription error for {node_str} on {self.endpoint}: {e}")
        except Exception as e:
            logging.error(f"Subscription setup error on {self.endpoint}: {e}")


    def is_connected(self):
        """Checks if the client is connected to the server."""
        if self.client:
            try:
                return self.client.uaclient.session is not None and self.client.uaclient.session.active
            except Exception:
                return False
        return False
class SubHandler:
    """Handles OPC UA data changes."""
    
    def __init__(self, sensor_pairs, sensors, handle_time_difference):
        self.sensor_pairs = sensor_pairs
        self.sensors = sensors
        self.handle_time_difference = handle_time_difference

    def datachange_notification(self, node, val, data):
        node_str = node.nodeid.to_string()
        node_name = node_str.split(';s=')[-1]  # Extract node name
        timestamp = data.monitored_item.Value.SourceTimestamp

        # Update sensor state if node is in sensors dictionary
        if node_name in self.sensors:
            self.sensors[node_name]["previous_state"] = self.sensors[node_name]["current_state"]
            self.sensors[node_name]["current_state"] = val
            self.sensors[node_name]["timestamp"] = timestamp

        # Iterate over sensor pairs
        for sensor_list in self.sensor_pairs.values():
            for sensor in sensor_list:
                # Check if this node matches any sensor name (including mappings)
                if node_name in (sensor["start_name"], sensor["end_name"], sensor.get("device_type", "")):
                    self.handle_time_difference(sensor, self.sensors)
                    return
                elif "mappings" in sensor:
                    for mapping in sensor["mappings"].values():
                        if node_name in (mapping["start_name"], mapping["end_name"]):
                            self.handle_time_difference(sensor, self.sensors)
                            return

