from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from azure.cosmos import CosmosClient, exceptions
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import joblib
import os
from datetime import datetime
import uvicorn

# FastAPI app
app = FastAPI()

# Azure configuration
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

BLOB_CONNECTION_STRING = ""
BLOB_CONTAINER_NAME = ""

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

# Function to fetch data from Cosmos DB
def fetch_data_from_cosmos(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # Query all the data from the container
    query = f"""SELECT * FROM c 
    WHERE c.organization_id = '{organization_id}' 
    AND c.unit_id = '{unit_id}' 
    AND c.machine_id = '{machine_id}' 
    AND c.sensor_id = '{sensor_id}' """
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    # Convert to DataFrame
    df = pd.DataFrame(items)
    print(f"fetched {len(df)} data from the cosmos related to the {organization_id}, {machine_id}, {sensor_id}")
    return df

# Function to train the Isolation Forest model
def train_model(df):
    features = ["temperature","minute", "hour","day","month", "year", "day_of_week", "is_weekend","rolling_mean_temp", "rolling_std_temp", "temp_lag_1s"]
    
    # Feature engineering and data preparation
    X = df[features]
    
    # Standardization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X_scaled)
    
    return model, scaler

# Function to save the model to Azure Blob Storage
def save_model_to_blob(model, model_type, organization_id, unit_id, machine_id, sensor_id):
    model_name = f"{organization_id}_{unit_id}_{machine_id}_{sensor_id}_{model_type}.pkl"
    
    # Save model to a local file
    with open(model_name, "wb") as f:
        joblib.dump(model, f)
    
    # Create a BlobServiceClient
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=f"{organization_id}/{unit_id}/{machine_id}/{sensor_id}/{model_type}.pkl")
    
    # Upload the model file to Blob Storage
    with open(model_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    os.remove(model_name)

# Load model from Azure Blob Storage
def load_model_from_azure(organization_id, unit_id, machine_id, sensor_id, model_type):
    model_name = f"{organization_id}_{unit_id}_{machine_id}_{sensor_id}_{model_type}.pkl"
    
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=f"{organization_id}/{unit_id}/{machine_id}/{sensor_id}/{model_type}.pkl")
    
    # Download the model file from Blob Storage
    with open(model_name, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    # Load the model from the file
    model = joblib.load(model_name)
    
    os.remove(model_name)
    print(f"Model loaded from {model_name} (downloaded from Azure Blob Storage)")
    
    return model

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

class TrainingInput(BaseModel):
    organization_id: str
    unit_id: str
    machine_id: str
    sensor_id: str    

class TrainingOutput(BaseModel):
    code: int
    msg: str
    
# API to trigger training and replace the running model
@app.post("/train_anomaly_model", response_model=TrainingOutput)
def train_and_store_model(data: TrainingInput):

    # Fetch data from Cosmos DB
    df = fetch_data_from_cosmos(organization_id=data.organization_id, unit_id=data.unit_id, machine_id=data.machine_id, sensor_id=data.sensor_id)

    # Train the new model
    model, scaler = train_model(df)

    # Save the new model to Blob Storage and update the running model
    save_model_to_blob(model, model_type="anomaly", organization_id=data.organization_id, unit_id=data.unit_id, machine_id=data.machine_id, sensor_id=data.sensor_id)
    
    save_model_to_blob(scaler, model_type="scaler", organization_id=data.organization_id, unit_id=data.unit_id, machine_id=data.machine_id, sensor_id=data.sensor_id)
    
    return TrainingOutput(code=200, msg="Model trained and saved to the azure blob")

@app.post("/predict_anomaly", response_model=AnomalyDetectionOutput)
def predict_anomaly(data: AnomalyDetectionInput):
    
    model = load_model_from_azure(data.organization_id, data.unit_id, data.machine_id, data.sensor_id, 'anomaly')
    scaler = load_model_from_azure(data.organization_id, data.unit_id, data.machine_id, data.sensor_id, 'scaler')
    
    # Convert input data to numpy array
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
    
    # Scale input data
    instance_scaled = scaler.transform(instance.reshape(1, -1))
    
    # Predict using Isolation Forest
    prediction = model.predict(instance_scaled)
    
    return AnomalyDetectionOutput(is_anomaly=(prediction[0] == -1), organization_id=data.organization_id, unit_id=data.unit_id, machine_id=data.machine_id, sensor_id=data.sensor_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)