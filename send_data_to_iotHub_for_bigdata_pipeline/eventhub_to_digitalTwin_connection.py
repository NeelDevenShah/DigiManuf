# Added the code for sending the data to iotHub and then retrieveing the data from eventHub, had made the events trigger to the EventHub from the iotHub portal

import asyncio
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.eventhub.aio import EventHubConsumerClient
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

def update_twin_property(twin_id, property_name, property_value):
    print(property_value)
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
    
    # The actual telemetry data is in the 'body' field, which is Base64 encoded
    encoded_body = event_data[0]['data']['body']
    
    # Decode the Base64 body
    decoded_body = base64.b64decode(encoded_body).decode('utf-8')
    
    # Parse the decoded body as JSON
    telemetry_data = json.loads(decoded_body)
    
   # Decode the Base64 body
    decoded_body = base64.b64decode(encoded_body).decode('utf-8')
    
    # Parse the decoded body as JSON
    telemetry_data = json.loads(decoded_body)
    
    print("Decoded telemetry data:")
    print(json.dumps(telemetry_data, indent=2))
    
    print("-" * 50)  # Print a separator line for clarity

    print("Starting the process to update data to digital twin")
    print(telemetry_data["deviceId"])
    update_twin_property(twin_id=telemetry_data["deviceId"], property_name="temperature", property_value=telemetry_data["temperature"])
    update_twin_property(twin_id=telemetry_data["deviceId"], property_name="humidity", property_value=telemetry_data["humidity"])
    
    print("process to update data to digital twin completed")

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