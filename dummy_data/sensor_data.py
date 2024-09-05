from azure.cosmos import CosmosClient, PartitionKey
import pandas as pd
import numpy as np
import os

# Azure Cosmos DB configuration
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

# Function to generate dummy data with precise datetime features
def generate_dummy_data_with_datetime(num_samples=1000):
    # Generate a range of datetime values, for example over a period of a day
    start_datetime = pd.to_datetime("2024-01-01 00:00:00")
    datetime_values = pd.date_range(start=start_datetime, periods=num_samples, freq='S')
    
    # Random temperature values
    temperature = np.random.normal(loc=20, scale=5, size=num_samples)

    # Feature extraction from datetime
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
        'is_weekend': datetime_values.dayofweek >= 5  # True if Saturday or Sunday
    })

    # Rolling mean and standard deviation (simulated for demonstration)
    df['rolling_mean_temp'] = df['temperature'].rolling(window=10, min_periods=1).mean()
    df['rolling_std_temp'] = df['temperature'].rolling(window=10, min_periods=1).std().fillna(0)
    df['temp_lag_1s'] = df['temperature'].shift(1).fillna(df['temperature'].iloc[0])

    return df

def upload_data_to_cosmos(df):
    # Create a Cosmos client
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)

    # Create or get the database
    database = client.create_database_if_not_exists(id=DATABASE_NAME)

    # Create or get the container
    container = database.create_container_if_not_exists(
        id=CONTAINER_NAME,
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400
    )

    # Upload each row in the DataFrame to Cosmos DB
    for i, row in df.iterrows():
        item = row.to_dict()
        item['id'] = str(i)  # Adding an 'id' field as required by Cosmos DB
        container.upsert_item(item)

    print(f"Data uploaded to Azure Cosmos DB container '{CONTAINER_NAME}'.")

# Generate the dummy data
dummy_data = generate_dummy_data_with_datetime(num_samples=10)

# Save the dummy data to a CSV file if needed
dummy_data.to_csv('dummy_data.csv', index=False)
dummy_data = pd.read_csv("dummy_data.csv")
upload_data_to_cosmos(dummy_data)
os.remove('dummy_data.csv')