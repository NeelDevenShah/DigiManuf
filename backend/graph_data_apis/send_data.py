from azure.cosmos import CosmosClient
import pandas as pd
from datetime import datetime, timedelta
import pandas as pd
import pyodbc


# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

SQL_SERVER = "your_sql_server.database.windows.net"
SQL_DATABASE = "your_database"
SQL_USERNAME = "your_username"
SQL_PASSWORD = "your_password"
SQL_DRIVER = "{ODBC Driver 17 for SQL Server}"

# SQL Server connection string
SQL_CONNECTION_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server;DATABASE=your_database;UID=your_username;PWD=your_password"

# TODO SQL Schema
# CREATE TABLE sensor_categories (
#     id INT PRIMARY KEY IDENTITY(1,1),
#     organization_id VARCHAR(50) NOT NULL,
#     machine_id VARCHAR(50) NOT NULL,
#     sensor_id VARCHAR(50) NOT NULL,
#     category VARCHAR(50) NOT NULL,
#     created_at DATETIME DEFAULT GETDATE(),
#     updated_at DATETIME DEFAULT GETDATE(),
#     CONSTRAINT UC_OrganizationMachineSensor UNIQUE (organization_id, machine_id, sensor_id)
# );

# # Fetch data for a specific time range
# # start_time = datetime(2023, 5, 1, 0, 0, 0)
# # end_time = datetime(2023, 5, 2, 0, 0, 0)
# # result = fetch_and_format_data('org123', 'machine456', 'sensor789', start_time, end_time)
def fetch_anomaly_data_for_sensors(organization_id: str, machine_id: str, sensor_id: str, start_time: datetime = None, end_time: datetime = None):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Set time range
    if start_time is None or end_time is None:
        end_time = datetime.now() - timedelta(minutes=30)
        start_time = end_time - timedelta(hours=24)
    
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    # Query data for the specified time range
    query = f"""SELECT * FROM c 
                WHERE c.organization_id = '{organization_id}' 
                AND c.machine_id = '{machine_id}' 
                AND c.sensor_id = '{sensor_id}' 
                AND c.datetime >= '{start_time_str}'
                AND c.datetime <= '{end_time_str}'"""
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from {start_time_str} to {end_time_str} for {organization_id}, {machine_id}, {sensor_id}")

    # Process data into 10-minute intervals
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    df.sort_index(inplace=True)

    # Resample to 10-minute intervals
    resampled = df.resample('10T').agg({
        'value': 'mean',
        'is_anomaly': lambda x: any(x)
    })

    # Format data for JSON output
    time_series_data = []
    for timestamp, row in resampled.iterrows():
        time_series_data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'value': row['value'],
            'is_anomaly': bool(row['is_anomaly'])
        })

    # Prepare the final JSON output
    output = {
        'organization_id': organization_id,
        'machine_id': machine_id,
        'sensor_id': sensor_id,
        'data': time_series_data
    }

    return output

def fetch_sensor_categories(organization_id: str, machine_id: str):
    conn = pyodbc.connect(SQL_CONNECTION_STRING)
    cursor = conn.cursor()
    
    query = """
    SELECT sensor_id, category
    FROM sensor_categories
    WHERE organization_id = ? AND machine_id = ?
    """
    
    cursor.execute(query, (organization_id, machine_id))
    categories = {row.sensor_id: row.category for row in cursor.fetchall()}
    
    cursor.close()
    conn.close()
    
    return categories

# Can be called for specifci machine by passing specific machine_id, or can be passed based on the organization_id
def fetch_anomaly_data_for_sensors_by_category(organization_id: str, machine_id: str, start_time: datetime = None, end_time: datetime = None):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Set time range
    if start_time is None or end_time is None:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
    
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    # Query data for the specified time range
    query = f"""SELECT * FROM c 
                WHERE c.organization_id = '{organization_id}' 
                AND c.machine_id = '{machine_id}' 
                AND c.datetime >= '{start_time_str}'
                AND c.datetime <= '{end_time_str}'"""
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from {start_time_str} to {end_time_str} for {organization_id}, {machine_id}")

    # Fetch sensor categories
    sensor_categories = fetch_sensor_categories(organization_id, machine_id)
    df['category'] = df['sensor_id'].map(sensor_categories)

    # Process data into 10-minute intervals
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    df.sort_index(inplace=True)

    # Group by category and resample to 10-minute intervals
    grouped = df.groupby('category')
    category_data = {}

    for category, group in grouped:
        resampled = group.resample('10T').agg({
            'value': 'mean',
            'is_anomaly': lambda x: any(x)
        })
        
        time_series_data = []
        for timestamp, row in resampled.iterrows():
            time_series_data.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'value': row['value'],
                'is_anomaly': bool(row['is_anomaly'])
            })
        
        category_data[category] = time_series_data

    # Prepare the final JSON output
    output = {
        'organization_id': organization_id,
        'machine_id': machine_id,
        'data': category_data
    }

    return output