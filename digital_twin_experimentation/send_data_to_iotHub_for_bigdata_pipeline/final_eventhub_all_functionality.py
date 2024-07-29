# Added the code for sending the data to iotHub and then retrieveing the data from eventHub, had made the events trigger to the EventHub from the iotHub portal

import asyncio
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.eventhub.aio import EventHubConsumerClient
from azure.storage.blob import BlobServiceClient
from azure.eventhub.extensions.checkpointstoreblobaio import (
    BlobCheckpointStore,
)
from azure.digitaltwins.core import DigitalTwinsClient
import json
import base64

# Define the Key Vault URL
key_vault_url = "https://newvaultneel.vault.azure.net/"

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a SecretClient to interact with the Key Vault
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

BLOB_STORAGE_CONNECTION_STRING = str(secret_client.get_secret("blob-connection-string").value)
BLOB_CHECKPOINT_CONTAINER_NAME = str(secret_client.get_secret("checkpoint-container-name").value)
BLOB_SENSOR_CONTAINER_NAME = str(secret_client.get_secret("sensordata-container-name").value)
EVENT_HUB_CONNECTION_STR = str(secret_client.get_secret("eventhub-conneciton-string").value)
EVENT_HUB_NAME = str(secret_client.get_secret("eventhub-name").value)

# Initialize the Digital Twins client
url = str(secret_client.get_secret(name="digital-twin-host-name").value)
credential = DefaultAzureCredential()
dt_client = DigitalTwinsClient(url, credential)

# Create a BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)

def create_hierarchical_path(device_id, timestamp_str):
    # Parse the timestamp string
    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    
    # Format the datetime into the hierarchical structure (up to minutes)
    hierarchical_time = dt.strftime("%Y/%m/%d/%H/%M")
    
    # Extract seconds for the file name
    seconds = dt.strftime("%S")
    
    # Combine device ID and hierarchical time
    folder_path = f"{device_id}/{hierarchical_time}"
    
    # Create file name with seconds
    file_name = f"data_{seconds}.json"
    
    return folder_path, file_name

def update_twin_property(twin_id, property_name, property_value):
    patch = [
        {
            "op": "replace",
            "path": f"/{property_name}",
            "value": float(property_value)
        }
    ]
    dt_client.update_digital_twin(twin_id, patch)
    print(f"Updated {property_name} of twin {twin_id} to {property_value}")


async def on_event(partition_context, event):
    print(f"Received event from partition: {partition_context.partition_id}")
    print(f"Sequence number: {event.sequence_number}")
    print(f"Offset: {event.offset}")
    print(f"Enqueued time: {event.enqueued_time}")
    
    # Parse the event body as JSON
    event_data = json.loads(event.body_as_str())
    encoded_body = event_data[0]['data']['body']
    decoded_body = base64.b64decode(encoded_body).decode('utf-8')
    telemetry_data = json.loads(decoded_body)
    
    print("Decoded telemetry data:")
    print(json.dumps(telemetry_data, indent=2))

    update_twin_property(twin_id=telemetry_data["deviceId"], property_name="temperature", property_value=telemetry_data["temperature"])
    update_twin_property(twin_id=telemetry_data["deviceId"], property_name="humidity", property_value=telemetry_data["humidity"])
    
    print("Process to update data to digital twin completed")
    
    # Save the message to Azure Blob Storage
    # Create the hierarchical path and file name
    folder_path, file_name = create_hierarchical_path(telemetry_data['deviceId'], telemetry_data['timestamp'])
    blob_client = blob_service_client.get_blob_client(container=BLOB_SENSOR_CONTAINER_NAME, blob=f"{folder_path}/{file_name}")

    blob_client.upload_blob(json.dumps(telemetry_data), overwrite=True)
    print("Saved message to Blob Storage")
    
    print("-" * 50)  # Print a separator line for clarity

    # Update the checkpoint
    await partition_context.update_checkpoint(event)

async def main():
    # Create an Azure blob checkpoint store to store the checkpoints.
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        BLOB_STORAGE_CONNECTION_STRING, BLOB_CHECKPOINT_CONTAINER_NAME
    )

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR,
        consumer_group="$Default",
        eventhub_name=EVENT_HUB_NAME,
        checkpoint_store=checkpoint_store,
    )
    async with client:
        # Call the receive method. Read from the beginning of the
        # partition (starting_position: "-1")
        await client.receive(on_event=on_event, starting_position="-1")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Run the main method.
    loop.run_until_complete(main())