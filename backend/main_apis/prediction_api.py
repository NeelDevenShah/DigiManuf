from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import joblib
from prophet import Prophet
from datetime import datetime
import os
import uvicorn

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

def fetch_data_from_cosmos(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    try:
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
        print(f"fetched {len(df)} data from the cosmos related to the {organization_id}, {machine_id}, {sensor_id}")
        return df
    
    except:
        return pd.DataFrame()

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

def train_model(df):
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.rename(columns={'timestamp': 'ds', 'temperature': 'y'})

    model = Prophet(yearly_seasonality=True, daily_seasonality=True)
    model.fit(df)

    return model

def save_model_to_blob(model, organization_id, unit_id, machine_id, sensor_id):
    model_type = "prediction"
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

@app.post("/train_prediction_model")
def train_and_store_model(data: TrainingInput):

    df = fetch_data_from_cosmos(organization_id = data.organization_id, unit_id=data.unit_id, machine_id = data.machine_id, sensor_id = data.sensor_id)
    
    if not df.empty:
    
        model = train_model(df)
        save_model_to_blob(model, organization_id = data.organization_id, unit_id=data.unit_id, machine_id = data.machine_id, sensor_id = data.sensor_id)
        
        return TrainingOutput(code=200, msg="Model trained and saved to the azure blob")
    
    return

@app.post("/predict_values")
def predict_values(data: PredictionInput):
    try:
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
    except:
        train_and_store_model(TrainingInput(organization_id=data.organization_id, unit_id=data.unit_id, machine_id=data.machine_id, sensor_id=data.sensor_id))
        return

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)