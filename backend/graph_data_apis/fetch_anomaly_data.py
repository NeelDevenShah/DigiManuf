# Micro-service-3

from azure.cosmos import CosmosClient
import pandas as pd
from datetime import datetime, timedelta
import pandas as pd
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi.responses import JSONResponse
from azure.cosmos import CosmosClient
from pymongo import MongoClient
from bson.objectid import ObjectId
import asyncio

app = FastAPI()

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"
LOG_CONTAINER_NAME = "log-container"
SENSOR_PRED_CONTAINER_NAME = "sensor-predictions"

client = MongoClient("")
db = client['digimanuf']

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

# TESTED: OK
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

# TESTED: OK
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
                AND c.datetime <= '{end_time_str}'
                AND c.anomaly_model_prediction
                """
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from {start_time_str} to {end_time_str} for {organization_id}, {machine_id}, {sensor_id}")

    if 'datetime' in df.columns and 'temperature' in df.columns and 'anomaly_model_prediction' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)

        time_series_data = []
        for index, row in df.iterrows():
            time_series_data.append(TimeSeriesData(
                timestamp=index,
                value=row['temperature'],
                is_anomaly=bool(row['anomaly_model_prediction'])
            ))

        return SensorDataOutput(
            organization_id=organization_id,
            unit_id=unit_id,
            machine_id=machine_id,
            sensor_id=sensor_id,
            data=time_series_data
        )
    else:
        return

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
    
@app.post("/fetch_sensor_categories")
def fetch_sensor_categories_api(request: SensorCategoryRequest):
    categories = fetch_sensor_categories(
        organization_id=request.organization_id,
        unit_id=request.unit_id,
        machine_id=request.machine_id
    )
    
    if not categories:
        return 
    
    return categories

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

# TESTED: OK
async def fetch_sensor_categories(organization_id: str, unit_id: str = None, machine_id: str = None):
    try:
        query = {"organization": ObjectId(organization_id)}
        if unit_id:
            query["unit"] = ObjectId(unit_id)

        if machine_id:
            query["machine"] = ObjectId(machine_id)

        sensors = db.sensors.find(query)
        categories = {str(sensor["_id"]): sensor["type"] for sensor in sensors}
        return categories

    except Exception as e:
        print(f"Error: {e}")
        return

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

# TESTED: OK
def fetch_sensor_ids_by_categories(organization_id: str, sensor_categories: list, unit_id: str = None, machine_id: str = None):
    try:
        # Step 1: Build the query with the organization ID and sensor categories
        query = {
            "organization": ObjectId(organization_id),
            "type": {"$in": sensor_categories}  # Matching the categories
        }

        if unit_id:
            query["unit"] = ObjectId(unit_id)
        if machine_id:
            query["machine"] = ObjectId(machine_id)

        sensors = db.sensors.find()
        categories = {str(sensor["_id"]): sensor["type"] for sensor in sensors}
        return categories

        # Step 4: Create a dictionary of sensor IDs and their categories
        sensor_data = {str(sensor._id): sensor.type for sensor in sensors}

        return sensor_data

    except Exception as e:
        print(f"Error: {e}")
        return {}

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

# For testing purpose only
async def main():
    # result = await fetch_sensor_categories("6704ef4787e2e83f2d915f04", "6704f1e426b62d9e3fd24ff6", "6704efcb87e2e83f2d915f3f")
    # result = await fetch_sensor_categories("6704ef4787e2e83f2d915f04", "6704f1e426b62d9e3fd24ff6")
    # result = await fetch_sensor_categories("6704ef4787e2e83f2d915f04")
    
    
    result = fetch_sensor_ids_by_categories("6704ef4787e2e83f2d915f04", ["fire"])
    print(result)

# For testing purpose only
# if __name__ == "__main__":
#     asyncio.run(main())

# Bydeault, use this one
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)