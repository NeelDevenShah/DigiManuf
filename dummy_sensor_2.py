import random
import time
from azure.iot.device import IoTHubDeviceClient, Message
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json

# Define the Key Vault URL
key_vault_url = "https://key-valut-digitaltwin.vault.azure.net/"

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a SecretClient to interact with the Key Vault
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Replace with your IoT Hub device connection string
CONNECTION_STRING = secret_client.get_secret("iot-device-2")
STORAGE_CONNECTION_STRING = secret_client.get_secret("blob-storage-string")
CONTAINER_NAME = secret_client.get_secret("blob-container-name")

# Create an IoT Hub client
iot_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

# Create a BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

def send_telemetry(sensor_id):
    while True:
        # Generate random telemetry data
        temperature = random.uniform(20.0, 30.0)
        humidity = random.uniform(30.0, 70.0)
        
        # Create the message payload
        message_payload = {
            "deviceId": sensor_id,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": time.time()
        }
        
        # Send the message to IoT Hub
        message = Message(json.dumps(message_payload))
        iot_client.send_message(message)
        print(f"Sent message to IoT Hub: {message_payload}")
        
        # Save the message to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=f"{sensor_id}/{time.time()}.json")
        blob_client.upload_blob(json.dumps(message_payload), overwrite=True)
        print(f"Saved message to Blob Storage: {message_payload}")
        
        # Wait for 5 seconds before sending the next message
        time.sleep(5)

if __name__ == "__main__":
    sensor = 'dummySensor2'
    send_telemetry(sensor)
    print(sensor)

