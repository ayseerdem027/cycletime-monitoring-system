import Influxhandler as IH
import logging
import sensors as SEN

sensor_pairs = SEN.sensor_pairs

def handle_time_difference(pair, sensors):
    """Calculates time difference between two sensors, using mappings if applicable."""

    device_type = pair.get("device_type")
    device_value = None
    normalized_value = None

    if device_type:
        device_value = sensors.get(device_type, {}).get("current_state")
        if isinstance(device_value, str):
            device_value = device_value.strip()
            normalized_value = device_value.upper()

        if not device_value:
            return

    start_sensor = pair["start_name"]
    end_sensor = pair["end_name"]
    start_default = pair["start_default"]
    end_default = pair["end_default"]

    if "mappings" in pair and normalized_value:
        mappings = {k.strip().upper(): v for k, v in pair["mappings"].items()}
        if normalized_value in mappings:
            mapping = mappings[normalized_value]
            start_sensor = mapping["start_name"]
            end_sensor = mapping["end_name"]
            start_default = mapping["start_default"]
            end_default = mapping["end_default"]

    # Fetch sensor data
    start = sensors.get(start_sensor)
    end = sensors.get(end_sensor)

    if not start or not end:
        print(f"[{pair['station']}] Missing sensor data for start: {start_sensor}, end: {end_sensor}")
        return

    if start["current_state"] == start["previous_state"] and end["current_state"] == end["previous_state"]:
        return

    if start["movement_start_timestamp"] is None:
        if start["previous_state"] == start_default and start["current_state"] != start_default:
            start["event_processed"] = False
            start["movement_start_timestamp"] = start["timestamp"]
        return

    if start["event_processed"]:
        return

    if end["previous_state"] != end_default and end["current_state"] == end_default:
        time_diff_ms = (end["timestamp"] - start["movement_start_timestamp"]).total_seconds() * 1000

        if not (0 < time_diff_ms < 600_000):
            start["movement_start_timestamp"] = None
            return

        station = pair["station"]
        line_name = next((key for key, value in sensor_pairs.items() if pair in value), None)

        IH.PostOPCUAdata2(
            "Zeitdifferenz",
            time_diff_ms,
            {"pair_name": station},
            {"assembly_line": line_name},
            {"device_type": device_value if device_value else ""}
        )

        start["event_processed"] = True
        start["movement_start_timestamp"] = None
