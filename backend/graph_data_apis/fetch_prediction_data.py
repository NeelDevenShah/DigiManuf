from azure.cosmos import CosmosClient
import pandas as pd
from datetime import datetime, timedelta
import pandas as pd
from azure.cosmos import CosmosClient
import uvicor
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import JSONResponsen

# TODO: Testing
# TODO: Central Server Start, Instead of the different ones from different places

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

def fetch_data_from_cosmos(organization_id: str, unit_id: str, machine_id: str, sensor_id: str, start_date: datetime, end_date: datetime):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    query = f"""SELECT c.datetime, c.temperature as value FROM c 
    WHERE c.organization_id = '{organization_id}' 
    AND c.unit_id = '{unit_id}' 
    AND c.machine_id = '{machine_id}' 
    AND c.sensor_id = '{sensor_id}'
    AND c.datetime >= '{start_date.isoformat()}'
    AND c.datetime <= '{end_date.isoformat()}'"""
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified criteria")
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    
    return [TimeSeriesData(datetime=row['datetime'].strftime('%Y-%m-%d %H:%M:%S'), value=row['value']) for _, row in df.iterrows()]

@app.post("/fetch-sensor-values")
def fetch_values_between_time_period(sensor_data: DataRequest):
    start_date = sensor_data.start_date
    end_date = sensor_data.end_date

    if not start_date and not end_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
    elif start_date and not end_date:
        end_date = datetime.now()
    elif not start_date and end_date:
        start_date = end_date - timedelta(hours=24)
        if start_date > datetime.now():
            start_date = datetime.now()

    data = fetch_data_from_cosmos(sensor_data.organization_id, sensor_data.unit_id, sensor_data.machine_id, sensor_data.sensor_id, start_date, end_date)
    
    return DataResponse(
        organization_id=sensor_data.organization_id,
        unit_id=sensor_data.unit_id,
        machine_id=sensor_data.machine_id,
        sensor_id=sensor_data.sensor_id,
        data=data
    )
    
###############################  
    
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
    
    if request.start_time and request.end_time:
        query += f" AND c.prediction_time BETWEEN '{request.start_time.isoformat()}' AND '{request.end_time.isoformat()}'"
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    time_series_data = [TimeSeriesData(
        datetime=row['prediction_time'].strftime('%Y-%m-%d %H:%M:%S'),
        value=row['prediction_value']
    ) for row in sorted(items, key=lambda x: x['prediction_time'])]

    return time_series_data

##################################

@app.post("/fetch_combined_data", response_model=DataResponse)
def fetch_combined_data_endpoint(request: DataRequest):
    centre_period = datetime.now()
    first_start_period = first_period_end - timedelta(hours=24)
    
    sensor_data.start_date = first_period_start
    sensor_data.end_date = first_period_end
    
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
    uvicorn.run(app, host="0.0.0.0", port=8000)