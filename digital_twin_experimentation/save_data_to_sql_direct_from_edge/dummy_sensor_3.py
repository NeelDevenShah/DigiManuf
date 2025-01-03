import random
import time
import datetime
from azure.digitaltwins.core import DigitalTwinsClient
from azure.iot.device import IoTHubDeviceClient, Message
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
import pyodbc

# Define the Key Vault URL
key_vault_url = "https://new-vault-neel.vault.azure.net/"

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a SecretClient to interact with the Key Vault
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Replace with your IoT Hub device connection string
CONNECTION_STRING = str(secret_client.get_secret("iot-device-3").value)

# Create an IoT Hub client
# iot_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

# Initialize the Digital Twins client
url = str(secret_client.get_secret(name="digital-twin-conn-url").value)
credential = DefaultAzureCredential()
client = DigitalTwinsClient(url, credential)

def update_twin_property(twin_id="Sensor1", property_name="", property_value=0):
    patch = [
        {
            "op": "replace",
            "path": f"/{property_name}",
            "value": property_value
        }
    ]
    client.update_digital_twin(twin_id, patch)
    print(f"Updated {property_name} of twin {twin_id} to {property_value}")

def send_telemetry(sensor_id, connection_string, insert_data_query):
   # Create a new connection for each iteration
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
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
            # message = Message(json.dumps(message_payload))
            # iot_client.send_message(message)
            print("Sent message to IoT Hub")

            # Convert the datetime to a format SQL Server can understand
            sql_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

            data = [(message_payload["deviceId"], message_payload["temperature"], message_payload["humidity"], sql_timestamp)]

            cursor.executemany(insert_data_query, data)
            connection.commit()
            print("Data inserted into SQL database")
            
            update_twin_property(property_name="temperature", property_value=message_payload["temperature"])
            update_twin_property(property_name="humidity", property_value=message_payload["humidity"])

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Wait for 2 seconds before sending the next message
        time.sleep(4)

if __name__ == "__main__":
    sensor = 'dummySensor3'
    # Insert data into the table
    insert_data_query = """
    INSERT INTO SensorData (deviceId, temperature, humidity, timestamp)
    VALUES (?, ?, ?, ?)
    """

    # Connection string
    connection_string = str(secret_client.get_secret("azure-sql-connection-url").value)

    send_telemetry(sensor, connection_string, insert_data_query)