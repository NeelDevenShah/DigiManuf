from azure.cosmos import CosmosClient, PartitionKey
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Azure Cosmos DB configuration
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"

def generate_dummy_data_with_datetime(num_samples=1000, organization_id="001", unit_id="001", machine_id="001", sensor_id="002"):
    start_datetime = pd.to_datetime("2024-01-01 00:00:00")
    datetime_values = pd.date_range(start=start_datetime, periods=num_samples, freq='s')
    
    temperature = np.random.normal(loc=20, scale=5, size=num_samples)

    df = pd.DataFrame({
        'datetime': datetime_values,
        'temperature': temperature,
        'second': datetime_values.second,
        'minute': datetime_values.minute,
        'hour': datetime_values.hour,
        'day': datetime_values.day,
        'month': datetime_values.month,
        'year': datetime_values.year,
        'day_of_week': datetime_values.dayofweek,  # Monday=0, Sunday=6
        'is_weekend': datetime_values.dayofweek >= 5,  # True if Saturday or Sunday
        'organization_id': organization_id,
        'unit_id': unit_id,
        'machine_id': machine_id,
        'sensor_id': sensor_id
    })

    df['rolling_mean_temp'] = df['temperature'].rolling(window=10, min_periods=1).mean()
    df['rolling_std_temp'] = df['temperature'].rolling(window=10, min_periods=1).std().fillna(0)
    df['temp_lag_1s'] = df['temperature'].shift(1).fillna(df['temperature'].iloc[0])

    return df

def upload_data_to_cosmos(df):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.create_database_if_not_exists(id=DATABASE_NAME)
    container = database.create_container_if_not_exists(
        id=CONTAINER_NAME,
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400
    )

    for i, row in df.iterrows():
        item = row.to_dict()
        
        datetime_format = '%Y-%m-%d %H:%M:%S'
        datetime_obj = datetime.strptime(item['datetime'], datetime_format)
        
        formatted_datetime = datetime_obj.strftime('%Y_%m_%dT%H_%M_%S')

        item['id'] = f"{item['organization_id']}_{item['unit_id']}_{item['machine_id']}_{item['sensor_id']}_date_{formatted_datetime}"
        container.upsert_item(item)

    print(f"Data uploaded to Azure Cosmos DB container '{CONTAINER_NAME}'.")

dummy_data = generate_dummy_data_with_datetime(num_samples=100, organization_id="org001", unit_id="unt001", machine_id="mac002", sensor_id="sen002")

dummy_data.to_csv('dummy_data.csv', index=False)
dummy_data = pd.read_csv("dummy_data.csv")
upload_data_to_cosmos(dummy_data)
os.remove('dummy_data.csv')