import time
import logging
import sensors as SEN
from EPManager import EPManager
from time_difference_calc import handle_time_difference
import json
import os
from dotenv import load_dotenv
load_dotenv()
# Load sensor pairs
sensor_pairs = SEN.sensor_pairs

# Load configuration from .env
endpoints = json.loads(os.getenv("ENDPOINTS"))
endpoint_lines = json.loads(os.getenv("ENDPOINT_LINES"))
namespaces = json.loads(os.getenv("NAMESPACES"))
device_types = json.loads(os.getenv("DEVICE_TYPES"))
# Extract endpoint lines for each endpoint
ep1_lines = endpoint_lines["ep1"]

# Build endpoint configuration
endpoint_config = {
    endpoints["ep1"]: [
        f"ns={namespaces[pair]};s={sensor_name}"
        for pair, values in sensor_pairs.items() if pair in ep1_lines
        for sensor in values
        for sensor_name in (
            [sensor["start_name"], sensor["end_name"]]
            + [mapping["start_name"] for mapping in sensor.get("mappings", {}).values()]
            + [mapping["end_name"] for mapping in sensor.get("mappings", {}).values()]
        )
    ] + [
        device_types[pair]
        for pair, values in sensor_pairs.items() if pair in ep1_lines
        for sensor in values
        if sensor.get("device_type")
    ]
}

# Sensor states 
sensors = {
    sensor_name: {
        "previous_state": None,
        "current_state": None,
        "timestamp": None,
        "movement_start_timestamp": None,
        "event_processed": False,
    }
    for values in sensor_pairs.values()  # Iterate over the lists of sensors
    for sensor in values  # Iterate over individual sensor dictionaries
    for sensor_name in [
        sensor["start_name"], 
        sensor["end_name"], 
        *([sensor["device_type"]] if "device_type" in sensor else []),
        *(
            [mapping["start_name"] for mapping in sensor.get("mappings", {}).values()] +
            [mapping["end_name"] for mapping in sensor.get("mappings", {}).values()]
            if "mappings" in sensor else []
        )
    ]
    if sensor_name  # Ensure sensor_name is not empty
}

def main():
     
    manager = EPManager(endpoint_config, sensor_pairs, sensors, handle_time_difference)
    manager.connect_all()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        manager.disconnect_all()
        raise

if __name__ == "__main__":
    main()
