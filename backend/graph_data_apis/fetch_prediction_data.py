# Micro-service-4

from azure.cosmos import CosmosClient
import pandas as pd
from datetime import datetime, timedelta
import pandas as pd
from azure.cosmos import CosmosClient
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi.responses import JSONResponse

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"
LOG_CONTAINER_NAME = "log-container"
SENSOR_PRED_CONTAINER_NAME = "sensor-predictions"

app = FastAPI()

class TimeSeriesData(BaseModel):
    datetime: str
    value: float

class DataRequest(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
class DataResponse(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str
    data: List[TimeSeriesData]

# TODO: Not working properly the second part of items
def fetch_data_from_cosmos(organization_id: str, unit_id: str, machine_id: str, sensor_id: str, start_time: datetime, end_time: datetime):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    query = f"""SELECT c.datetime, c.temperature AS temp FROM c 
    WHERE c.organization_id = "{organization_id}"
    AND c.unit_id = "{unit_id}" 
    AND c.machine_id = "{machine_id}"
    AND c.sensor_id = "{sensor_id}"
    AND c.datetime >= "{start_time}"
    AND c.datetime <= "{end_time}" """
    # Make sure the datetime is in format "2024-01-01 00:00:00"

    # Execute the query with parameters
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified criteria")
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    
    return [TimeSeriesData(datetime=row['datetime'].strftime('%Y-%m-%d %H:%M:%S'), value=row['temp']) for _, row in df.iterrows()]

@app.post("/fetch-sensor-values")
def fetch_values_between_time_period(sensor_data: DataRequest):
    # Make sure the datetime is in format "2024-01-01 00:00:00"
    start_time = getattr(sensor_data, 'start_time', None)
    end_time = getattr(sensor_data, 'end_time', None)

    if not start_time and not end_time:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
    elif start_time and not end_time:
        end_time = datetime.now()
    elif not start_time and end_time:
        start_time = end_time - timedelta(hours=24)
        if start_time > datetime.now():
            start_time = datetime.now()

    data = fetch_data_from_cosmos(sensor_data.organization_id, sensor_data.unit_id, sensor_data.machine_id, sensor_data.sensor_id, start_time, end_time)
    
    return DataResponse(
        organization_id=sensor_data.organization_id,
        unit_id=sensor_data.unit_id,
        machine_id=sensor_data.machine_id,
        sensor_id=sensor_data.sensor_id,
        data=data
    )
    
@app.post("/fetch-sensor-predictions", response_model=DataResponse)
def get_predictions(request: DataRequest) -> List[TimeSeriesData]:
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(SENSOR_PRED_CONTAINER_NAME)
    
    query = f"""SELECT c.prediction_time, c.prediction_value FROM c 
    WHERE c.organization_id = '{request.organization_id}' 
    AND c.unit_id = '{request.unit_id}' 
    AND c.machine_id = '{request.machine_id}' 
    AND c.sensor_id = '{request.sensor_id}'"""
    
    # Make sure the datetime is in format "2024-01-01 00:00:00"
    if request.start_time and request.end_time:
        query += f" AND c.prediction_time BETWEEN '{request.start_time}' AND '{request.end_time}'"
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    time_series_data = []
    for row in sorted(items, key=lambda x: x['prediction_time']):
        prediction_time = pd.to_datetime(row['prediction_time'])
        
        time_series_data.append(TimeSeriesData(
            datetime=prediction_time.strftime('%Y-%m-%d %H:%M:%S'),
            value=row['prediction_value']
        ))
    return DataResponse(
        organization_id=request.organization_id,
        unit_id=request.unit_id,
        machine_id=request.machine_id,
        sensor_id=request.sensor_id,
        data=time_series_data)

@app.post("/fetch_combined_data", response_model=DataResponse)
def fetch_combined_data_endpoint(request: DataRequest):
    centre_period = datetime.now()
    first_start_period = first_period_end - timedelta(hours=24)
    
    sensor_data.start_time = first_period_start
    sensor_data.end_time = first_period_end
    
    original_values = fetch_values_between_time_period(sensor_data)
    first_period_data = original_values.data
    
    # Fetch the second 24 hours of data
    second_period_end = centre_period + timedelta(hours=24)
    
    prediction_request.start_time = centre_period
    prediction_request.end_time = second_period_end
    
    second_period_data = get_predictions(prediction_request)
    
    # Combine the two datasets
    combined_data = first_period_data + second_period_data
    
    return DataResponse(
        organization_id=sensor_data.organization_id,
        unit_id=sensor_data.unit_id,
        machine_id=sensor_data.machine_id,
        sensor_id=sensor_data.sensor_id,
        data=combined_data
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)