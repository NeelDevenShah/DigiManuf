import os
import json
from azure.identity import ClientSecretCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.storage.blob import BlobServiceClient
import logging

# Set up the Azure Digital Twins client
tenant_id = os.getenv('AZURE_TENANT_ID')
client_id = os.getenv('AZURE_CLIENT_ID')
client_secret = os.getenv('AZURE_CLIENT_SECRET')
adt_url = os.getenv('AZURE_DIGITAL_TWINS_URL')
storage_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')

credential = ClientSecretCredential(tenant_id, client_id, client_secret)
digital_twins_client = DigitalTwinsClient(adt_url, credential)
blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

def main(event: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                 event.get_body().decode('utf-8'))
    
    message = event.get_body().decode('utf-8')
    data = json.loads(message)

    # Assuming the message contains deviceId, temperature, and humidity
    device_id = data['deviceId']
    temperature = data['temperature']
    humidity = data['humidity']
    timestamp = data['timestamp']

    # Update the digital twin instance
    twin_id = device_id  # Ensure this matches your twin's ID
    patch = [
        {
            "op": "replace",
            "path": "/Temperature",
            "value": temperature
        },
        {
            "op": "replace",
            "path": "/Humidity",
            "value": humidity
        }
    ]

    digital_twins_client.update_digital_twin(twin_id, patch)
    
    # Save the message to Azure Blob Storage
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{device_id}/{timestamp}.json")
    blob_client.upload_blob(json.dumps(data), overwrite=True)
    logging.info(f"Saved message to Blob Storage: {data}")

