
import pandas as pd  # type: ignore
from influxdb_client import InfluxDBClient, Point  # type: ignore
from influxdb_client.client.write_api import SYNCHRONOUS  # type: ignore
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv  # type: ignore
import sys
import warnings
from influxdb_client.client.warnings import MissingPivotFunction  # type: ignore
from collections import defaultdict

sys.path.append('/shared_data')

from sensors import sensor_pairs # type: ignore
warnings.simplefilter("ignore", MissingPivotFunction)

sensors = sensor_pairs

load_dotenv()

# Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
ORG = os.getenv("INFLUXDB_ORG")
RAW_BUCKET = "CycleTime"
FILTERED_BUCKET = "FilteredCycleTime"

# Initialize InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=ORG)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

# A dictionary mapping `PAIR_NAME` to a list of `line` values
pair_to_line = defaultdict(list)
for key, value in sensor_pairs.items():
    for sensor in value:
        pair_to_line[sensor["station"]].append(key)

print(f"Pair to line mapping: {dict(pair_to_line)}")

# Fetch raw data
def fetch_raw_data(pair_name, start_time, end_time, line):
    query = f'''
        from(bucket: "{RAW_BUCKET}")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "time_difference")
        |> filter(fn: (r) => r["_field"] == "timeDifference")
        |> filter(fn: (r) => r["pair_name"] == "{pair_name}")
        |> filter(fn: (r) => r["assembly_line"] == "{line}")
    '''
    tables = query_api.query_data_frame(query)

    if isinstance(tables, list):
        tables = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()

    if tables.empty:
        print(f"No data found for {pair_name} (Line: {line}) in {RAW_BUCKET} from {start_time} to {end_time}")
    else:
        print(f"Found {len(tables)} data points for {pair_name} (Line: {line})")

    return tables

# Calculate limits
def calculate_limits(historical_data):
    if historical_data.empty:
        return None, None
    Q1 = historical_data["_value"].quantile(0.25)
    Q3 = historical_data["_value"].quantile(0.75)
    IQR = Q3 - Q1
    lower_limit = max(Q1 - 1.5 * IQR, 0)
    upper_limit = Q3 + 1.5 * IQR
    return lower_limit, upper_limit

# Filter real-time data
def filter_real_time_data(data, lower, upper):
    if data.empty or lower is None or upper is None:
        return pd.DataFrame()
    return data[(data["_value"] >= lower) & (data["_value"] <= upper)]

# Write filtered data
def write_filtered_data(data, pair_name, line):
    points = [
        Point("filtered_time_difference")
        .tag("pair_name", pair_name)
        .tag("assembly_line", line)
        .field("timeDifference", row["_value"])
        .time(row["_time"])
        for _, row in data.iterrows()
    ]
    write_api.write(bucket=FILTERED_BUCKET, org=ORG, record=points)

# Main script
if __name__ == "__main__":
    while True:
        current_time = datetime.now()
        for pair_name, lines in pair_to_line.items():
            for line in lines:
                historical_data = fetch_raw_data(pair_name, (current_time - timedelta(weeks=3)).isoformat() + "Z", current_time.isoformat() + "Z", line)
                lower, upper = calculate_limits(historical_data)
                real_time_data = fetch_raw_data(pair_name, (current_time - timedelta(minutes=2)).isoformat() + "Z", current_time.isoformat() + "Z", line)
                filtered = filter_real_time_data(real_time_data, lower, upper)
                if not filtered.empty:
                    write_filtered_data(filtered, pair_name, line)
        time.sleep(120)
