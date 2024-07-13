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

# Create a new table
create_table_query = """
CREATE TABLE SensorData (
    deviceId NVARCHAR(50),
    temperature FLOAT,
    humidity FLOAT,
    timestamp DATETIME
)
"""
cursor.execute(create_table_query)
connection.commit()
print("Table created successfully.")

# Insert data into the table
insert_data_query = """
INSERT INTO SensorData (deviceId, temperature, humidity, timestamp)
VALUES (?, ?, ?, ?)
"""
# Sample data
data = [
    ('device1', 23.5, 45.0, datetime.datetime.now()),
    ('device2', 24.0, 50.0, datetime.datetime.now()),
    ('device3', 22.5, 55.0, datetime.datetime.now())
]

cursor.executemany(insert_data_query, data)
connection.commit()
print("Data inserted successfully.")

# Close the connection
cursor.close()
connection.close()