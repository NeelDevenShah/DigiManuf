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

# FastAPI app
app = FastAPI()

# Azure configuration
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

BLOB_CONNECTION_STRING = ""
BLOB_CONTAINER_NAME = ""
BLOB_MODEL_NAME = "model_prediction.pkl"

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

# Function to fetch data from Cosmos DB
def fetch_data_from_cosmos(organization_id: str, machine_id: str, sensor_id: str):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # Query all the data from the container
    query = f"""SELECT * FROM c 
    WHERE c.organization_id = '{organization_id}' 
    AND c.machine_id = '{machine_id}' 
    AND c.sensor_id = '{sensor_id}' """
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    # Convert to DataFrame
    df = pd.DataFrame(items)
    print(f"fetched {len(df)} data from the cosmos related to the {organization_id}, {machine_id}, {sensor_id}")
    return df

# API to predict future sensor values
class PredictionInput(BaseModel):
    periods: int  # Number of future periods to predict
    start_timestamp: Optional[str] = None  # Optional start timestamp in ISO format
    organization_id: str
    machine_id: str
    sensor_id: str

class PredictionOutput(BaseModel):
    predictions: List[float]  # List of predicted values
    organization_id: str
    machine_id: str
    sensor_id: str

class TrainingInput(BaseModel):
    organization_id: str
    machine_id: str
    sensor_id: str
    
class TrainingOutput(BaseModel):
    code: int
    msg: str

# Function to train the Prophet model
def train_model(df):
    # Convert the DataFrame to a format compatible with Prophet
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.rename(columns={'timestamp': 'ds', 'temperature': 'y'})

    # Train the Prophet model with seasonality and trend
    model = Prophet(yearly_seasonality=True, daily_seasonality=True)
    model.fit(df)

    return model

# Function to save the model to Azure Blob Storage
def save_model_to_blob(model, organization_id , machine_id, sensor_id):
    model_type = "prediction"
    model_name = f"{organization_id}_{machine_id}_{sensor_id}_{model_type}.pkl"
    
    # Save model and scaler to a local file
    with open(model_name, "wb") as f:
        joblib.dump(model, f)
    
    # Create a BlobServiceClient
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=f"{organization_id}/{machine_id}/{sensor_id}/{model_type}.pkl")
    
    # Upload the model file to Blob Storage
    with open(model_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    os.remove(model_name)

# Load model from Azure Blob Storage
def load_model_from_azure(organization_id, machine_id, sensor_id, model_type):
    model_name = f"{organization_id}_{machine_id}_{sensor_id}_{model_type}.pkl"
    
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=f"{organization_id}/{machine_id}/{sensor_id}/{model_type}.pkl")
    
    # Download the model file from Blob Storage
    with open(model_name, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    # Load the model from the file
    model = joblib.load(model_name)
    
    os.remove(model_name)
    print(f"Model loaded from {model_name} (downloaded from Azure Blob Storage)")
    
    return model

# API to trigger training and replace the running model
@app.post("/train_prediction_model", response_model=TrainingOutput)
def train_and_store_model(data: TrainingInput):

    # Fetch data from Cosmos DB
    df = fetch_data_from_cosmos(organization_id = data.organization_id, machine_id = data.machine_id, sensor_id = data.sensor_id)

    # Train the new model
    model = train_model(df)

    # Save the new model to Blob Storage and update the running model
    save_model_to_blob(model, organization_id = data.organization_id, machine_id = data.machine_id, sensor_id = data.sensor_id)
    
    return TrainingOutput(code=200, msg="Model trained and saved to the azure blob")

@app.post("/predict_values", response_model=PredictionOutput)
def predict_values(data: PredictionInput):
    
    model = load_model_from_azure(data.organization_id, data.machine_id, data.sensor_id, 'prediction')

    # Create a future dataframe with the specified number of periods
    if data.start_timestamp:
        start_date = pd.to_datetime(data.start_timestamp)
    else:
        # Use the current time for the start_date
        start_date = pd.Timestamp(datetime.now())

        # Optionally, if you want to ensure that the start_date is rounded to the nearest hour, you can do:
        start_date = start_date.ceil('H')

    future = model.make_future_dataframe(periods=data.periods, freq='H', include_history=False)
    future['ds'] = pd.date_range(start=start_date, periods=data.periods, freq='H')

    # Predict future values
    forecast = model.predict(future)

    # Extract the predicted values (yhat)
    predictions = forecast['yhat'].tolist()
    
    return PredictionOutput(predictions=predictions, organization_id=data.organization_id, machine_id=data.machine_id, sensor_id=data.sensor_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)