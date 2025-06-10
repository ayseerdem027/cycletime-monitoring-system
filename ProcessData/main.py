
import time
import influxhandling as IH

import EndpointHandling as EH
import xml.etree.ElementTree as ET
import logging
import sys
import mls as ML

mls = ML.mls

def main():

    try:
        while True:
            for ml in mls.values():
                ml_namespace = ml['namespace']
                ml_node = ml['complexTag']

                # Retrieve the complexTag value
                ml_values = EH.LoadNode(ml_namespace, ml_node)
                

                robo_fault = EH.LoadNode(ml_namespace, ml['robo_fault'])
                robo_busy = EH.LoadNode(ml_namespace, ml['robo_busy'])

                ml['complexTag_value'] = ml_values

                if ml_values is None:
                    logging.warning(f"No value for complexTag {ml['complexTag']}")
                    continue
                
                # Parse the XML response
                try:
                    root = ET.fromstring(ml_values)
                except ET.ParseError as e:
                    logging.error(f"XML ParseError for complexTag {ml['complexTag']}: {e}")
                    continue
                
                # Extract fields
                fields = {item.find('Name').text: item.find('Value').text for item in root.findall('Item')}

                # Convert fields into a sorted tuple for duplicate detection
                sorted_fields = tuple(sorted(fields.items()))

                if "processed_values" not in ml:
                    ml["processed_values"] = set()

                if sorted_fields in ml["processed_values"]:
                    logging.info(f"Duplicate data for {ml['name']}, skipping.")
                    continue

                ml["processed_values"].add(sorted_fields)
                sorted_fields = dict(sorted_fields)
                energy_value = float(sorted_fields.get(ml['energiewert'], "0"))
                electricity_value = float(sorted_fields.get(ml['stromwert'], "0"))
                
                # Only print if energy value is NOT 0
                if energy_value != 0 and electricity_value != 0:

                    # Post the data to InfluxDB
                    IH.post_opcua_data(measurement_name="EOLData", fields=sorted_fields, tags={"ML": ml['name']})
                IH.post_robodata(robo_fault, robo_busy, ml['name'])
                logging.debug(f"Robo Fault: {robo_fault} | Robo Busy: {robo_busy} | ML: {ml['name']}")   


            time.sleep(6)
            
    except Exception as e:
        logging.info(f"An error occured {e}")

if __name__ == "__main__":
    main()
