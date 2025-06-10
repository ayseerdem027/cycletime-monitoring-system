
from influxdb_client.client.write_api import SYNCHRONOUS # type: ignore
from influxdb_client import InfluxDBClient, Point, WritePrecision # type: ignore
import os
 
import warnings
from influxdb_client.client.warnings import MissingPivotFunction # type: ignore
warnings.simplefilter("ignore", MissingPivotFunction)
 

token = "cZ_r9Nnk4d4TMLBA0GwbhRP3WMARy3bpT7WmeBF5A4SuFtI8hEsM9SkONFYnsnppJSr5JFr0Ew1eUQC4Jq2uww=="
org = "Hilti"
url = "http://influxdb2:8086" 
BUCKET = "ProcessData"
host = "influxdb"


write_client = InfluxDBClient(url=url, token=token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)
 

def is_number(value):
    try:
        float(value)  # Try converting to float
        return True
    except ValueError:
        return False

def post_opcua_data(measurement_name, fields, tags=None):
    if fields:
        point = Point(measurement_name)

        if tags:
            for tag_key, tag_value in tags.items():
                point = point.tag(tag_key, tag_value)

        # Process fields
        for name, value in fields.items():
            if isinstance(value, (int, float)):  
                # Already a number
                point = point.field(name, value)
            elif isinstance(value, str) and is_number(value):
                # Convert numeric strings to float
                point = point.field(name, float(value))
            else:
                # Store as string if it's not a number
                point = point.field(name, value)

        try:
            write_api.write(bucket=BUCKET, record=point, org=org)
            return 200  # Success
        except Exception as e:
            print("Error:", e)
            logging.error(f"Error writing to InfluxDB: {e}")
            return 400  # Error
    else:
        return 200  

def post_robodata(robofault, robobusy, ml_name):
    try:
        robofault_point = Point("opcua").tag("name", ml_name).field("Robo_Fault", bool(robofault))
        robobusy_point = Point("opcua").tag("name", ml_name).field("Robo_Busy", bool(robobusy))
        
        write_api.write(bucket=BUCKET, record=[robofault_point, robobusy_point])
        return {"Robo_Fault": robofault, "Robo_Busy": robobusy}
    except Exception as e:
        
        logging.error(f"Error writing Robo data to InfluxDB: {e}")
        return None

 