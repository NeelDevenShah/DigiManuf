# Added the code for sending the data to iotHub and then retrieveing the data from eventHub, had made the events trigger to the EventHub from the iotHub portal

import random
import time
import datetime
from azure.iot.device import IoTHubDeviceClient, Message
from azure.storage.blob import BlobServiceClient
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
import pyodbc

# Define the Key Vault URL
key_vault_url = "https://newvaultneel.vault.azure.net/"

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a SecretClient to interact with the Key Vault
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Replace with your IoT Hub device connection string
CONNECTION_STRING = str(secret_client.get_secret("iot-device-1").value)

# Create an IoT Hub client
iot_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

# Initialize the Digital Twins client
# url = str(secret_client.get_secret(name="digital-twin-conn-url").value)
# credential = DefaultAzureCredential()
# client = DigitalTwinsClient(url, credential)

# def update_twin_property(twin_id="Sensor3", property_name="", property_value=0):
#     patch = [
#         {
#             "op": "replace",
#             "path": f"/{property_name}",
#             "value": property_value
#         }
#     ]
#     client.update_digital_twin(twin_id, patch)
#     print(f"Updated {property_name} of twin {twin_id} to {property_value}")

def send_telemetry(sensor_id):
   # Create a new connection for each iteration
    while True:
        try:
            # Generate random telemetry data
            temperature = random.uniform(20.0, 30.0)
            humidity = random.uniform(30.0, 70.0)
            
            # Create the message payload
            current_time = datetime.datetime.utcnow()
            message_payload = {
                "deviceId": sensor_id,
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": current_time.isoformat()  # Use ISO format for IoT Hub message
            }
            
            # Send the message to IoT Hub
            message = Message(json.dumps(message_payload))
            iot_client.send_message(message)
            print("Sent message to IoT Hub")
            
            # update_twin_property(property_name="temperature", property_value=message_payload["temperature"])
            # update_twin_property(property_name="humidity", property_value=message_payload["humidity"])

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Wait for 2 seconds before sending the next message
        time.sleep(4)

if __name__ == "__main__":
    sensor = 'Sensor1'
    send_telemetry(sensor)