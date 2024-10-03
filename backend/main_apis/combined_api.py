from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import joblib
from prophet import Prophet
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import os
import shutil
import numpy as np

# ARCHIEVED, CURRENTLY THIS FILE IS NOT IN WORKING

app = FastAPI()

# Azure configuration
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"

BLOB_CONNECTION_STRING = ""
BLOB_CONTAINER_NAME = "dmcontainer"

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

class AnomalyDetectionInput(BaseModel):
    temperature: float
    second: int
    minute: int
    hour: int
    day: int
    month: int
    year: int
    day_of_week: int
    is_weekend: bool
    rolling_mean_temp: float
    rolling_std_temp: float
    temp_lag_1s: float
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str

class AnomalyDetectionOutput(BaseModel):
    is_anomaly: bool
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str
  
class PredictionInput(BaseModel):
    periods: int
    start_timestamp: Optional[str] = None
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str

class PredictionOutput(BaseModel):
    predictions: List[float]
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str
    
class TrainingInput(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str

class TrainingOutput(BaseModel):
    code: int
    msg: str

async def fetch_data_from_cosmos(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    query = f"""SELECT * FROM c 
    WHERE c.organization_id = '{organization_id}'
    AND c.unit_id = '{unit_id}' 
    AND c.machine_id = '{machine_id}' 
    AND c.sensor_id = '{sensor_id}' """
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    df = pd.DataFrame(items)
    return df
                
def download_from_azure(blob_service_client, container_name, blob_prefix, local_dir):
    blobs = container_client.list_blobs(name_starts_with=blob_prefix)

    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        download_file_path = os.path.join(local_dir, os.path.basename(blob.name))
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

async def train_and_save_models(df, organization_id, unit_id, machine_id, sensor_id):
    # Training the prediction model
    prediction_model = train_prediction_model(df)
    save_model_to_azure(prediction_model, organization_id, unit_id, machine_id, sensor_id, 'prediction')

    anomaly_model, scaler = train_anomaly_detection_model(df)
    save_model_to_azure(anomaly_model, organization_id, unit_id, machine_id, sensor_id, 'anomaly')
    save_model_to_azure(scaler, organization_id, unit_id, machine_id, sensor_id, 'scaler')

    return

def train_prediction_model(df):
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.rename(columns={'timestamp': 'ds', 'temperature': 'y'})
    model = Prophet(yearly_seasonality=True, daily_seasonality=True)
    model.fit(df)
    return model

def train_anomaly_detection_model(df):
    features = ["temperature", "minute", "hour", "day", "month", "year", "day_of_week", "is_weekend", "rolling_mean_temp", "rolling_std_temp", "temp_lag_1s"]
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X_scaled)
    return model, scaler

def save_model_to_azure(model, organization_id, unit_id, machine_id, sensor_id, model_type):

    model_name = f"{organization_id}_{unit_id}_{machine_id}_{sensor_id}_{model_type}.pkl"
    
    with open(model_name, "wb") as f:
        joblib.dump(model, f)
    
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=f"{organization_id}/{unit_id}/{machine_id}/{sensor_id}/{model_type}.pkl")
    
    with open(model_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    os.remove(model_name)

def load_model_from_azure(organization_id, unit_id, machine_id, sensor_id, model_type):
    model_name = f"{organization_id}_{unit_id}_{machine_id}_{sensor_id}_{model_type}.pkl"
    
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=f"{organization_id}/{unit_id}/{machine_id}/{sensor_id}/{model_type}.pkl")
    
    with open(model_name, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    model = joblib.load(model_name)
    
    os.remove(model_name)
    print(f"Model loaded from {model_name} (downloaded from Azure Blob Storage)")
    
    return model

@app.post("/train_models", response_model=TrainingOutput)
async def train_models(data: TrainingInput):
    df = await fetch_data_from_cosmos(data.organization_id, data.unit_id, data.machine_id, data.sensor_id)
    await train_and_save_models(df, data.organization_id, data.unit_id, data.machine_id, data.sensor_id)
    return TrainingOutput(code=200, msg="Model trained and saved to the azure blob")

@app.post("/predict_values", response_model=PredictionOutput)
async def predict_values(data: PredictionInput):
    
    model = load_model_from_azure(data.organization_id, data.unit_id, data.machine_id, data.sensor_id, 'prediction')
    
    if data.start_timestamp:
        start_date = pd.to_datetime(data.start_timestamp)
    else:
        start_date = pd.Timestamp(datetime.now())

        start_date = start_date.ceil('H')

    future = model.make_future_dataframe(periods=data.periods, freq='H', include_history=False)
    future['ds'] = pd.date_range(start=start_date, periods=data.periods, freq='H')

    forecast = model.predict(future)

    predictions = forecast['yhat'].tolist()

    return PredictionOutput(predictions=predictions, organization_id=data.organization_id, unit_id=data.unit_id, machine_id=data.machine_id, sensor_id=data.sensor_id)

@app.post("/detect_anomalies", response_model=AnomalyDetectionOutput)
async def detect_anomalies(data: AnomalyDetectionInput):
    model = load_model_from_azure(data.organization_id, data.unit_id, data.machine_id, data.sensor_id, 'anomaly')
    scaler = load_model_from_azure(data.organization_id, data.unit_id, data.machine_id, data.sensor_id, 'scaler')
    
    instance = np.array([
        data.temperature, 
        data.minute, 
        data.hour,
        data.day,
        data.month, 
        data.year, 
        data.day_of_week, 
        data.is_weekend,
        data.rolling_mean_temp, 
        data.rolling_std_temp, 
        data.temp_lag_1s
    ])
    
    instance_scaled = scaler.transform(instance.reshape(1, -1))
    
    prediction = model.predict(instance_scaled)
    is_anomaly=(prediction[0] == -1)
    
    return AnomalyDetectionOutput(is_anomaly= is_anomaly, organization_id= data.organization_id, unit_id=data.unit_id, machine_id= data.machine_id, sensor_id= data.sensor_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
