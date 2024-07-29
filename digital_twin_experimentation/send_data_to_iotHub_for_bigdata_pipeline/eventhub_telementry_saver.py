# Added the code for sending the data to iotHub and then retrieveing the data from eventHub, had made the events trigger to the EventHub from the iotHub portal

import asyncio
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import (
    BlobCheckpointStore,
)
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
    
    print("Decoded telemetry data:")
    print(json.dumps(telemetry_data, indent=2))
    
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