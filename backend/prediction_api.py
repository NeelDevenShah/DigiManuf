from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import joblib
from prophet import Prophet
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
BLOB_MODEL_NAME = "model_prediction.pkl"

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
def save_model_to_blob(model, is_backup=False):
    filename = BLOB_MODEL_NAME if not is_backup else f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_model.pkl"
    
    # Save model to a local file
    with open(filename, "wb") as f:
        joblib.dump(model, f)

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
    with open("model_prediction.pkl", "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    # Load the model from the file
    model = joblib.load("model_prediction.pkl")
    return model

# API to trigger training and replace the running model
@app.post("/train_prediction_model")
def train_and_store_model():
    global model

    # Fetch data from Cosmos DB
    df = fetch_data_from_cosmos()

    # Train the new model
    model = train_model(df)

    # Save the new model to Blob Storage and update the running model
    save_model_to_blob(model)
    
    return {"message": "Model trained, updated, and saved to blob storage"}

# API to predict future sensor values
class PredictionInput(BaseModel):
    periods: int  # Number of future periods to predict
    start_timestamp: Optional[str] = None  # Optional start timestamp in ISO format

class PredictionOutput(BaseModel):
    predictions: List[float]  # List of predicted values

@app.post("/predict_values", response_model=PredictionOutput)
def predict_values(data: PredictionInput):
    global model
    if model is None:
        return {"error": "Model not loaded. Train the model first."}

    # Create a future dataframe with the specified number of periods
    if data.start_timestamp:
        start_date = pd.to_datetime(data.start_timestamp)
    else:
        # Use the latest date from the training data if no start_timestamp is provided
        df = fetch_data_from_cosmos()
        df['timestamp'] = pd.to_datetime(df['datetime'])
        start_date = df['timestamp'].max() + pd.Timedelta(hours=1)  # Start from the next hour

    future = model.make_future_dataframe(periods=data.periods, freq='H', include_history=False)
    future['ds'] = pd.date_range(start=start_date, periods=data.periods, freq='H')

    # Predict future values
    forecast = model.predict(future)

    # Extract the predicted values (yhat)
    predictions = forecast['yhat'].tolist()
    
    return PredictionOutput(predictions=predictions)

if __name__ == "__main__":
    import uvicorn
    
    # Load model on startup
    try:
        model = load_model_from_blob()
        print("Model loaded from blob storage")
    except Exception as e:
        print("Failed to load model. Error:", e)
        model = None
    
    uvicorn.run(app, host="0.0.0.0", port=8000)