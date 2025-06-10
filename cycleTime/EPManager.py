import logging
import threading
import time
from EPHandler import EPlogin, SubHandler
from dotenv import load_dotenv
import os
load_dotenv()

class EPManager:
    """Manages multiple OPC UA connections to different endpoints."""
    
    def __init__(self, endpoint_config, sensor_pairs, sensors, handle_time_difference):
        self.endpoint_config = endpoint_config
        self.sensor_pairs = sensor_pairs
        self.sensors = sensors
        self.handle_time_difference = handle_time_difference
        self.connections = {}  # Store connections per endpoint
        self.threads = []  # Store threads for monitoring connections

    def connect_all(self):
        """Establish connections for all endpoints."""
        for endpoint, nodes in self.endpoint_config.items():
            connection = EPlogin(endpoint)
            success = connection.connect()
            if success:
                handler = SubHandler(self.sensor_pairs, self.sensors, self.handle_time_difference)
                connection.subscribe(nodes, handler)
                print(f"Subscribed to nodes {nodes}")
                self.connections[endpoint] = connection
                thread = threading.Thread(target=self.monitor_connection, args=(connection, nodes, handler), daemon=True)
                thread.start()
                self.threads.append(thread)
            else:
                logging.error(f"Failed to connect to {endpoint}")

    def monitor_connection(self, connection, nodes, handler):
        """Continuously checks connection and reconnects if lost."""
        while True:
            try:
                if not connection.is_connected():
                    logging.warning(f"Connection lost for {connection.endpoint}, attempting reconnection...")

                    # Try reconnecting
                    if connection.connect():
                        logging.debug(f"Reconnected to {connection.endpoint}")

                        # Re-subscribe to nodes
                        connection.subscribe(nodes, handler)
                    else:
                        logging.error(f"Reconnection failed for {connection.endpoint}")
                
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logging.error(f"Error in connection monitor for {connection.endpoint}: {e}")


    def disconnect_all(self):
        """Disconnects from all endpoints."""
        for connection in self.connections.values():
            connection.disconnect()
        logging.info("Disconnected from all endpoints.")
