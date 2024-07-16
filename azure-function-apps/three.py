import azure.functions as func
import logging
import pyodbc
import datetime
import json

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp()

# Establish the connection
connection = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:newserverneel.database.windows.net,1433;Database=newserverneel;Uid=azureuser;Pwd={Neelshah@1610};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
connection = pyodbc.connect(connection)
cursor = connection.cursor()

# Insert data into the table
insert_data_query = """
INSERT INTO SensorData (deviceId, temperature, humidity, timestamp)
VALUES (?, ?, ?, ?)
"""

# # Close the connection
# cursor.close()
# connection.close()

# Here, make the connection named newhubneel_events_IOTHUB in the azure funcitons -> environment variables -> App Settings -> Add
@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="eventhubname",
                               connection="newhubneel_events_IOTHUB") 
def eventhub_trigger1(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                azeventhub.get_body().decode('utf-8'))
    try:
        message_data = json.loads(azeventhub.get_body().decode('utf-8'))
        logging.info('Message extracted: %s', message_data)

        # Extract values from the dictionary
        device_id = message_data.get('deviceId')
        temperature = message_data.get('temperature')
        humidity = message_data.get('humidity')
        timestamp = message_data.get('timestamp')
        
        data = [(device_id, temperature, humidity, timestamp)]
        
        cursor.executemany(insert_data_query, data)
        connection.commit()
        print("Data inserted successfully.")
        logging.info("Data added to the database successfully")

    except Exception as e:
        logging.error('Error processing the event: %s', str(e))