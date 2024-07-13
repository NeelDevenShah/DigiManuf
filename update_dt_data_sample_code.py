from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import time

# Define the Key Vault URL
key_vault_url = "https://key-valut-digitaltwin.vault.azure.net/"

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a SecretClient to interact with the Key Vault
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Initialize the Digital Twins client
url = str(secret_client.get_secret(name="digital-twin-conn-url", version="23a626c281034fa0ad27f43d3fc5bd30").value)
credential = DefaultAzureCredential()
client = DigitalTwinsClient(url, credential)

def get_data_from_edge_device():
    # This function would implement the logic to retrieve data from your edge device
    # It could involve reading from an IoT Hub, Event Hub, or other data source
    # For this example, we'll just return a dummy value
    return {"temperature": 25.5, "humidity": 200}

def update_twin_property(twin_id, property_name, property_value):
    patch = [
        {
            "op": "replace",
            "path": f"/{property_name}",
            "value": property_value
        }
    ]
    client.update_digital_twin(twin_id, patch)
    print(f"Updated {property_name} of twin {twin_id} to {property_value}")

def main():
    twin_id = "Sensor1"
    # Get data from edge device
    edge_data = get_data_from_edge_device()
    
    # Update twin properties based on received data
    for property_name, property_value in edge_data.items():
        update_twin_property(twin_id, property_name, property_value)
    
    # Wait for some time before next update
    # time.sleep(60)  # Update every 60 seconds

if __name__ == "__main__":
    main()