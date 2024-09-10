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

app = FastAPI()

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

# ################################

class TimeSeriesData(BaseModel):
    datetime: str
    value: float

class SensorData(BaseModel):
    sensor_id: str
    data: List[TimeSeriesData]

class PredictionDataResponse(BaseModel):
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

@app.post("/fetch-predicted-values")
def fetch_predicted_values_between_time_period(sensor_data: SensorData):
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

    data = fetch_data_from_cosmos(organization_id, unit_id, machine_id, sensor_id, start_date, end_date)
    
    return AnomalyDataResponse(
        organization_id=organization_id,
        unit_id=unit_id,
        machine_id=machine_id,
        sensor_id=sensor_id,
        data=data
    )

def fetch_predicted_values_betweenn_time_period():
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)