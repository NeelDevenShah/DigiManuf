from azure.cosmos import CosmosClient
import pandas as pd
from datetime import datetime, timedelta
import pandas as pd
import pyodbc
import uvicor
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import JSONResponsen

# TODO: Testing

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

SQL_SERVER = ""
SQL_DATABASE = ""
SQL_USERNAME = ""
SQL_PASSWORD = ""
# TODO, check driver with the old code
SQL_DRIVER = "{ODBC Driver 17 for SQL Server}"

# SQL Server connection string
SQL_CONNECTION_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server;DATABASE=your_database;UID=your_username;PWD=your_password"

# TODO SQL Schema
# CREATE TABLE sensor_categories (
#     id INT PRIMARY KEY IDENTITY(1,1),
#     organization_id VARCHAR(50) NOT NULL,
#     unit_id VARCHAR(50) NOT NULL,
#     machine_id VARCHAR(50) NOT NULL,
#     sensor_id VARCHAR(50) NOT NULL,
#     category VARCHAR(50) NOT NULL,
#     created_at DATETIME DEFAULT GETDATE(),
#     updated_at DATETIME DEFAULT GETDATE(),
#     CONSTRAINT UC_OrganizationMachineSensor UNIQUE (organization_id, unit_id, machine_id, sensor_id)
# );

# TODO SQL Schema
# CREATE TABLE machine_categories (
#     id INT PRIMARY KEY IDENTITY(1,1),
#     organization_id VARCHAR(50) NOT NULL,
#     unit_id VARCHAR(50) NOT NULL,
#     machine_id VARCHAR(50) NOT NULL,
#     category VARCHAR(50) NOT NULL,
#     created_at DATETIME DEFAULT GETDATE(),
#     updated_at DATETIME DEFAULT GETDATE(),
#     CONSTRAINT UC_OrganizationMachineSensor UNIQUE (organization_id, unit_id, machine_id)
# );

############# For fetching anomaly the data related to the particular sensor

class SensorAnomalyDataRequest(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
class TimeSeriesData(BaseModel):
    timestamp: datetime
    value: float
    is_anomaly: bool

class SensorDataOutput(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str
    data: List[TimeSeriesData]

@app.post("/fetch_anomaly_data_for_sensors")
def fetch_anomaly_data_for_sensors_api(request: SensorAnomalyDataRequest):
    organization_id = request.organization_id
    unit_id = request.unit_id
    machine_id = request.machine_id
    sensor_id = request.sensor_id
    start_time = request.start_time
    end_time = request.end_time
    
    output = fetch_anomaly_data_for_sensors(organization_id, unit_id, machine_id, sensor_id, start_time, end_time)
    return output

def fetch_anomaly_data_for_sensors(organization_id: str, unit_id: str, machine_id: str, sensor_id: str, start_time: datetime = None, end_time: datetime = None):
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
                AND c.unit_id = '{unit_id}' 
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
        # Use Pydantic model for time series data
        time_series_data.append(TimeSeriesData(
            timestamp=timestamp,  # Keep as a datetime object, Pydantic will handle formatting
            value=row['value'],
            is_anomaly=bool(row['is_anomaly'])
        ))

    # Prepare the final output using the Pydantic model
    output = SensorDataOutput(
        organization_id=organization_id,
        unit_id=unit_id,
        machine_id=machine_id,
        sensor_id=sensor_id,
        data=time_series_data
    )

# API and functions done


################### For fetching anomaly data related to the all sensor categories

class SensorCategoryRequest(BaseModel):
    organization_id: str
    unit_id: Optional[str] = None
    machine_id: Optional[str] = None

# Model for fetching anomaly data with optional date range
class AnomalyDataRequest(BaseModel):
    organization_id: str
    unit_id: Optional[str] = None
    machine_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
@app.post("/fetch_sensor_categories", response_model=SensorCategoryResponse)
def fetch_sensor_categories_api(request: SensorCategoryRequest):
    categories = fetch_sensor_categories(
        organization_id=request.organization_id,
        unit_id=request.unit_id,
        machine_id=request.machine_id
    )
    
    if not categories:
        return SensorCategoryResponse(message="No categories found for the specified criteria")
    
    return SensorCategoryResponse(sensor_categories=categories)

@app.post("/fetch_anomaly_data_for_sensors_by_all_category")
def fetch_anomaly_data_api(request: AnomalyDataRequest):
    # Set time range if not provided
    if request.start_time is None or request.end_time is None:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
    else:
        start_time = request.start_time
        end_time = request.end_time
    
    data = fetch_anomaly_data_for_sensors_by_all_category(
        organization_id=request.organization_id,
        unit_id=request.unit_id,
        machine_id=request.machine_id,
        start_time=start_time,
        end_time=end_time
    )
    
    if not data:
        return {"message": "No anomaly data found for the specified criteria"}
    
    return data

def fetch_sensor_categories(organization_id: str, unit_id: str = None, machine_id: str = None):
    conn = pyodbc.connect(SQL_CONNECTION_STRING)
    cursor = conn.cursor()

    # Base query
    query = """
    SELECT sensor_id, category
    FROM sensor_categories
    WHERE organization_id = ?
    """
    params = [organization_id]

    # Conditionally add unit_id and machine_id to the query if provided
    if unit_id:
        query += " AND unit_id = ?"
        params.append(unit_id)

    if machine_id:
        query += " AND machine_id = ?"
        params.append(machine_id)

    # Execute the query
    cursor.execute(query, params)
    categories = {row.sensor_id: row.category for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return categories

class SensorCategoryDataResponse(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    data: Dict[str, List[TimeSeriesData]] 

def fetch_anomaly_data_for_sensors_by_all_category(organization_id: str, unit_id: str = None, machine_id: str = None, start_time: datetime = None, end_time: datetime = None):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Set time range
    if start_time is None or end_time is None:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
    
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    # Base query
    query = f"""SELECT * FROM c 
                WHERE c.organization_id = '{organization_id}'
                AND c.datetime >= '{start_time_str}'
                AND c.datetime <= '{end_time_str}'"""

    # Conditionally add unit_id and machine_id if provided
    if unit_id:
        query += f" AND c.unit_id = '{unit_id}'"
    if machine_id:
        query += f" AND c.machine_id = '{machine_id}'"
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from {start_time_str} to {end_time_str} for {organization_id}")

    if df.empty:
        print("No data found for the specified criteria.")
        return None

    # Fetch sensor categories
    sensor_categories = fetch_sensor_categories(organization_id, unit_id, machine_id)
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
            time_series_data.append(TimeSeriesData(
                timestamp=timestamp,  # Keep as datetime, Pydantic will handle formatting
                value=row['value'],
                is_anomaly=bool(row['is_anomaly'])
            ))
        
        category_data[category] = time_series_data

    # Prepare the final output using Pydantic
    output = SensorCategoryDataResponse(
        organization_id=organization_id,
        unit_id=unit_id,
        machine_id=machine_id,
        data=category_data
    )

    return output


################## For fetching anomaly data related to the particular sensor categories

def fetch_sensor_ids_by_categories(organization_id: str, sensor_categories: list, unit_id: str = None, machine_id: str = None):
    conn = pyodbc.connect(SQL_CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Base query
    query = """
    SELECT sensor_id, category
    FROM sensor_categories
    WHERE organization_id = ?
    """
    params = [organization_id]

    # Conditionally add unit_id and machine_id to the query if provided
    if unit_id:
        query += " AND unit_id = ?"
        params.append(unit_id)

    if machine_id:
        query += " AND machine_id = ?"
        params.append(machine_id)

    # Add the sensor categories with placeholders
    placeholders = ','.join('?' for _ in sensor_categories)
    query += f" AND category IN ({placeholders})"
    params.extend(sensor_categories)

    # Execute the query with dynamic parameters
    cursor.execute(query, params)
    sensor_data = {row.sensor_id: row.category for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return sensor_data

class SensorCategoriesRequest(BaseModel):
    organization_id: str
    sensor_categories: List[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    unit_id: Optional[str] = None
    machine_id: Optional[str] = None

@app.post("/fetch-anomaly-data")
async def fetch_anomaly_data(request: SensorCategoriesRequest):
    # Extracting request parameters
    organization_id = request.organization_id
    sensor_categories = request.sensor_categories
    unit_id = request.unit_id
    machine_id = request.machine_id
    start_time = request.start_time
    end_time = request.end_time

    # Set time range if not provided
    if not start_time or not end_time:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)

    # Call the function that fetches anomaly data
    result = fetch_anomaly_data_for_sensors_by_categories(
        organization_id=organization_id,
        unit_id=unit_id,
        machine_id=machine_id,
        sensor_categories=sensor_categories,
        start_time=start_time,
        end_time=end_time
    )

    if result is None:
        return JSONResponse(status_code=404, content={"message": "No data found for the specified criteria."})

    return result

class SensorCategoryData(BaseModel):
    sensor_id: str
    data: List[TimeSeriesData]
    
class CategoryDataResponse(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    data: Dict[str, Dict[str, List[TimeSeriesData]]]

# Adjusted fetch_anomaly_data function to make unit_id and machine_id optional
def fetch_anomaly_data_for_sensors_by_categories(organization_id: str, sensor_categories: list, unit_id: Optional[str] = None, machine_id: Optional[str] = None, start_time: datetime = None, end_time: datetime = None):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # Set time range
    if start_time is None or end_time is None:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)

    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    # Fetch sensor IDs for the given categories
    sensor_data = fetch_sensor_ids_by_categories(organization_id, unit_id, machine_id, sensor_categories)

    if not sensor_data:
        print(f"No sensors found for categories: {sensor_categories}")
        return None

    # Construct the query dynamically
    sensor_id_condition = " OR ".join([f"c.sensor_id = '{sensor_id}'" for sensor_id in sensor_data.keys()])
    query = f"SELECT * FROM c WHERE c.organization_id = '{organization_id}'"

    # Add unit_id and machine_id to the query only if provided
    if unit_id:
        query += f" AND c.unit_id = '{unit_id}'"
    if machine_id:
        query += f" AND c.machine_id = '{machine_id}'"

    query += f" AND ({sensor_id_condition})"
    query += f" AND c.datetime >= '{start_time_str}' AND c.datetime <= '{end_time_str}'"

    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from {start_time_str} to {end_time_str} for {organization_id}, unit_id: {unit_id}, machine_id: {machine_id}")

    if df.empty:
        print("No data found for the specified criteria.")
        return None

    # Process data into 10-minute intervals
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    df.sort_index(inplace=True)

    # Add category information to the dataframe
    df['category'] = df['sensor_id'].map(sensor_data)

    # Group by category and sensor_id, then resample to 10-minute intervals
    grouped = df.groupby(['category', 'sensor_id'])
    category_data = {}

    for (category, sensor_id), group in grouped:
        resampled = group.resample('10T').agg({
            'value': 'mean',
            'is_anomaly': lambda x: any(x)
        })
        
        time_series_data = []
        for timestamp, row in resampled.iterrows():
            time_series_data.append(TimeSeriesData(
                timestamp=timestamp,  # Keep as datetime, Pydantic will handle formatting
                value=row['value'],
                is_anomaly=bool(row['is_anomaly'])
            ))

        if category not in category_data:
            category_data[category] = {}
        category_data[category][sensor_id] = time_series_data

    # Prepare the final output using Pydantic
    output = CategoryDataResponse(
        organization_id=organization_id,
        unit_id=unit_id,
        machine_id=machine_id,
        data=category_data
    )

    # Return the JSON representation of the output
    return output

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)