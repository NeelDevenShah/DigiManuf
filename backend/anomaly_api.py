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

# FastAPI app
app = FastAPI()

# Azure configuration
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

BLOB_CONNECTION_STRING = ""
BLOB_CONTAINER_NAME = ""
BLOB_MODEL_NAME = "model_anomaly.pkl"

# Function to fetch data from Cosmos DB
def fetch_data_from_cosmos():
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # Query all the data from the container
    query = "SELECT * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    # Convert to DataFrame
    df = pd.DataFrame(items)
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
def save_model_to_blob(model, scaler, is_backup=False):
    filename = BLOB_MODEL_NAME if not is_backup else f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_model_anomaly.pkl"
    
    # Save model and scaler to a local file
    with open(filename, "wb") as f:
        joblib.dump((model, scaler), f)

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=filename)
    
    # Upload the model file to Blob Storage
    with open(filename, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

# Function to load the model from Azure Blob Storage
def load_model_from_blob():
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=BLOB_MODEL_NAME)
    
    # Download the model file from Blob Storage
    with open("model_anomaly.pkl", "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    # Load the model from the file
    model, scaler = joblib.load("model_anomaly.pkl")
    return model, scaler

# API to trigger training and replace the running model
@app.post("/train_anomaly_model")
def train_and_store_model():
    global model, scaler

    # Fetch data from Cosmos DB
    df = fetch_data_from_cosmos()

    # Train the new model
    model, scaler = train_model(df)

    # Save the new model to Blob Storage and update the running model
    save_model_to_blob(model, scaler)
    
    return {"message": "Model trained, updated, and saved to blob storage"}

# API to predict anomaly
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

class AnomalyDetectionOutput(BaseModel):
    is_anomaly: bool

@app.post("/predict_anomaly", response_model=AnomalyDetectionOutput)
def predict_anomaly(data: AnomalyDetectionInput):
    global model, scaler
    if model is None or scaler is None:
        return {"error": "Model not loaded. Train the model first."}

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
    
    return AnomalyDetectionOutput(is_anomaly=(prediction[0] == -1))

if __name__ == "__main__":
    import uvicorn
    
    try:
        model, scaler = load_model_from_blob()
        print("Model loaded from blob storage")
    except Exception as e:
        print("Failed to load model. Error:", e)
        model, scaler = None, None
    
    uvicorn.run(app, host="0.0.0.0", port=8000)