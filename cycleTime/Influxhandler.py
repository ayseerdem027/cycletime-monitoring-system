from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WriteOptions
import os
import warnings
from influxdb_client.client.warnings import MissingPivotFunction
from dotenv import load_dotenv
import logging

warnings.simplefilter("ignore", MissingPivotFunction)
load_dotenv()

# Load Influx config
token = os.getenv("INFLUXDB_TOKEN")
url = os.getenv("INFLUXDB_URL")
org = os.getenv("INFLUXDB_ORG")
BUCKET = "CycleTime"


client = InfluxDBClient(url=url, token=token, org=org)


write_api = client.write_api(write_options=WriteOptions(
    batch_size=100,         # Write after 100 points
    flush_interval=1000,    # Or every 1 second
    jitter_interval=200,    # Helps smooth load on server
    retry_interval=5000     # Retry after 5s on failure
))

def PostOPCUAdata2(name, value, tags=None, tags2=None, tags3=None):
    point = Point("time_difference").tag("name", name).field("timeDifference", float(value))

    if tags:
        for key, tag_value in tags.items():
            point = point.tag(key, tag_value)

    if tags2:
        for key, value in tags2.items():
            point = point.tag(key, value)

    if tags3:
        for key, value in tags3.items():
            point = point.tag(key, value)

    try:
        write_api.write(bucket=BUCKET, record=point)
        return name, value
    except Exception as e:
        logging.error("Error:", e)
        return None, None
