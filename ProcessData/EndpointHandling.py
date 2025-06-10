
import time
import logging
from opcua import Client
logging.basicConfig(level=logging.ERROR)
class Keplogin:
    
    MAX_RETRIES = 100  
    
    def __init__(self):
        self.client = None
    
    def __enter__(self):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                self.client = Client("opc.tcp://THG-KEPWARED01.hilti.com:49320", timeout=50.0)
                self.client.session_timeout = 1800000  # 30 minutes in milliseconds
                self.client.connect()
                return self
            except Exception as e:
                retries += 1
                print(f"Error connecting (attempt {retries}/{self.MAX_RETRIES}): {e}")
                logging.error(f"Error connecting (attempt {retries}/{self.MAX_RETRIES}): {e}")
                time.sleep(100)  # Wait for a while before retrying
                
        print("Failed to establish connection after multiple attempts.")
        logging.error("Failed to establish connection after multiple attempts.")
        raise ConnectionError("Failed to establish connection after multiple attempts.")
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.client:
                self.client.disconnect()
        except Exception as e:
            print(f"Fehler beim Trennen: {e}")
            logging.info(f"Fehler beim Trennen: {e}")
    
    def getData(self, stringi):
        try:
            if self.client:
                node = self.client.get_node(stringi)
                return node.get_value()
            else:
                raise ValueError("Client is not connected")
        except Exception as e:
            logging.error(f"Error getting Data: {node} {e}")
    
def LoadNode(namespace, node):
    try:
        with Keplogin() as connection:
            stringi = f"ns={namespace};s={node}"
            value = connection.getData(stringi)
            return value
    except Exception as e:
        logging.error(f"Error loading node: {e}")
