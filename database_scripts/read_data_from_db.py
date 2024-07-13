import pyodbc
import datetime

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Define the key Vault URL
key_vault_url = "https://dtwin-keyvault.vault.azure.net/"

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a SecretClient to interact with the Key Vault
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Establish the connection
connection = str(secret_client.get_secret("azure-sql-connection-url").value)
connection = pyodbc.connect(connection)
cursor = connection.cursor()

read_data_query = """SELECT * FROM SensorData;"""

cursor.execute(read_data_query)
rows = cursor.fetchall()

# Print the results
print("Recent sensor data:")
for row in rows:
    print(f"Device ID: {row.deviceId}, Temperature: {row.temperature}°C, Humidity: {row.humidity}%, Timestamp: {row.timestamp}")
    
# Close the connection
cursor.close()
connection.close()