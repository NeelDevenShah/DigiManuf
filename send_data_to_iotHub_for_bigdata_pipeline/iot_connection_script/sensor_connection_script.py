# Added the code for sending the data to iotHub and then retrieveing the data from eventHub, had made the events trigger to the EventHub from the iotHub portal

import random
import time
import datetime
from azure.iot.device import IoTHubDeviceClient, Message
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

def send_telemetry(sensor_id):
    # Replace with your IoT Hub device connection string
    CONNECTION_STRING = str(secret_client.get_secret(f"iot-device-{sensor_id}").value)

    # Create an IoT Hub client
    iot_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    
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

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Wait for 4 seconds before sending the next message
        time.sleep(4)

if __name__ == "__main__":
    # As per the name in the azure iot hub and azure digital twin
    sensor_id = 'Sensor1'
    send_telemetry(sensor_id)