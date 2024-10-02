from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from datetime import datetime
from sklearn.ensemble import IsolationForest
from prophet import Prophet
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import joblib

# FOR FUTURE PLAN, CURRENTLY THIS FILE IS NOT IN WORKING
# TODO Debugging and editing

app = FastAPI()

# Azure configuration
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

BLOB_CONNECTION_STRING = ""
BLOB_CONTAINER_NAME = ""

ANOMALY_MODEL_NAME = "model_anomaly.pkl"
PREDICTION_MODEL_NAME = "model_prediction.pkl"


# TODO: Change the sql query
# Placeholder functions for fetching data and models
def fetch_sensor_data(organization_id: str, unit_id:str, machine_id: str, sensor_id: str, start_time: datetime, end_time: datetime):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # Query all the data from the container
    query = "SELECT * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    # Convert to DataFrame
    df = pd.DataFrame(items)
    return df

def load_anomaly_model():
    # Load pre-trained Isolation Forest model from Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=ANOMALY_MODEL_NAME)
    
    # Download the model file from Blob Storage
    with open("model_anomaly.pkl", "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    # Load the model from the file
    model, scaler = joblib.load("model_anomaly.pkl")
    return model, scaler

def load_prediction_model():
    # Load pre-trained Prophet model from Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=PREDICTION_MODEL_NAME)
    
    # Download the model file from Blob Storage
    with open("model_prediction.pkl", "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    # Load the model from the file
    model = joblib.load("model_prediction.pkl")
    return model

# API models
class MachineOverview(BaseModel):
    machine_id: str
    start_time: datetime
    end_time: datetime
    explanation: str
    avg_values: Dict[str, float]
    max_values: Dict[str, float]
    min_values: Dict[str, float]
    std_devs: Dict[str, float]

class AnomalyDetection(BaseModel):
    machine_id: str
    explanation: str
    anomalies: Dict[str, List[str]]  # sensor_id -> list of anomaly timestamps
    
class AnomalyDetectionInput(BaseModel):
    temperature: float
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

class Prediction(BaseModel):
    machine_id: str
    explanation: str
    predictions: Dict[str, List[float]]  # sensor_id -> list of predicted values

class MachineInsights(BaseModel):
    machine_id: str
    explanation: str
    trend: Dict[str, List[float]]  # sensor_id -> list of trend values
    seasonal: Dict[str, List[float]]  # sensor_id -> list of seasonal values
    anomalies: Dict[str, List[float]]  # sensor_id -> list of anomaly timestamps
    predictions: Dict[str, List[float]]  # sensor_id -> list of predicted values

# API to provide an overview of the machine's sensor data with explanations
@app.get("/machine_overview", response_model=MachineOverview)
def machine_overview(machine_id: str, start_time: datetime, end_time: datetime):
    data = fetch_sensor_data(machine_id, start_time, end_time)
    avg_values = data.mean().to_dict()
    max_values = data.max().to_dict()
    min_values = data.min().to_dict()
    std_devs = data.std().to_dict()
    
    explanation = (
        f"Overview of sensor data for machine {machine_id} from {start_time} to {end_time}.\n"
        f"On average, the sensors recorded the following values: {avg_values}.\n"
        f"The maximum recorded values were: {max_values}.\n"
        f"The minimum recorded values were: {min_values}.\n"
        f"The standard deviations of the sensors' data were: {std_devs}, indicating variability in the readings."
    )
    
    return MachineOverview(
        machine_id=machine_id,
        start_time=start_time,
        end_time=end_time,
        explanation=explanation,
        avg_values=avg_values,
        max_values=max_values,
        min_values=min_values,
        std_devs=std_devs
    )

# API to detect anomalies with explanations
@app.get("/machine_anomalies", response_model=AnomalyDetection)
def machine_anomalies(machine_id: str, start_time: datetime, end_time: datetime):
    global anomaly_model, anomaly_scaler
    if anomaly_model is None or anomaly_scaler is None:
        return {"error": "Model not loaded. Train the model first."}

    # Fetch data from the specified time range
    data = fetch_sensor_data(machine_id, start_time, end_time)
    
    anomalies = {}
    explanation_parts = []
    for sensor_id in data.columns:
        sensor_data = data[sensor_id].values
        sensor_data_df = pd.DataFrame(sensor_data, columns=["feature"])

        # Prepare the data for prediction
        scaled_data = anomaly_scaler.transform(sensor_data_df)
        
        # Predict anomalies
        anomaly_labels = anomaly_model.predict(scaled_data)
        anomaly_timestamps = data.index[anomaly_labels == -1].tolist()
        anomalies[sensor_id] = anomaly_timestamps
        explanation_parts.append(f"For sensor {sensor_id}, anomalies were detected at: {anomaly_timestamps}.")
    
    explanation = (
        f"Anomalies detected in sensor data for machine {machine_id} from {start_time} to {end_time}.\n" +
        "\n".join(explanation_parts)
    )
    
    return AnomalyDetection(machine_id=machine_id, explanation=explanation, anomalies=anomalies)

# API to predict future sensor values with explanations
@app.get("/machine_predictions", response_model=Prediction)
def machine_predictions(machine_id: str, periods: int = Query(24)):
    data = fetch_sensor_data(machine_id, datetime.now() - pd.DateOffset(days=30), datetime.now())
    
    predictions = {}
    explanation_parts = []
    for sensor_id in data.columns:
        sensor_df = pd.DataFrame({'ds': data.index, 'y': data[sensor_id]})
        prediction_model.fit(sensor_df)
        future = prediction_model.make_future_dataframe(periods=periods, freq='H')
        forecast = prediction_model.predict(future)
        predictions[sensor_id] = forecast['yhat'][-periods:].tolist()
        explanation_parts.append(
            f"Based on historical data, predictions for the next {periods} hours for sensor {sensor_id} are: {predictions[sensor_id]}."
        )
    
    explanation = (
        f"Future predictions of sensor values for machine {machine_id}.\n" +
        "\n".join(explanation_parts)
    )
    
    return Prediction(machine_id=machine_id, explanation=explanation, predictions=predictions)

# API to provide aggregated insights with explanations
@app.get("/machine_insights", response_model=MachineInsights)
def machine_insights(machine_id: str, periods: int = Query(24)):
    data = fetch_sensor_data(machine_id, datetime.now() - pd.DateOffset(days=30), datetime.now())
    
    trends = {}
    seasonals = {}
    anomalies = {}
    predictions = {}
    explanation_parts = []

    for sensor_id in data.columns:
        sensor_df = pd.DataFrame({'ds': data.index, 'y': data[sensor_id]})
        prediction_model.fit(sensor_df)
        forecast = prediction_model.predict(prediction_model.make_future_dataframe(periods=periods, freq='H'))

        # Extract trend and seasonal components
        trends[sensor_id] = forecast['trend'].tolist()
        seasonals[sensor_id] = forecast['seasonal'].tolist()

        # Detect anomalies
        sensor_data = data[sensor_id].values.reshape(-1, 1)
        anomaly_labels = anomaly_model.fit_predict(sensor_data)
        anomalies[sensor_id] = data.index[anomaly_labels == -1].tolist()

        # Store predictions
        predictions[sensor_id] = forecast['yhat'][-periods:].tolist()

        explanation_parts.append(
            f"For sensor {sensor_id}:\n"
            f"Trend data shows the following patterns: {trends[sensor_id]}.\n"
            f"Seasonal patterns identified as: {seasonals[sensor_id]}.\n"
            f"Anomalies were detected at: {anomalies[sensor_id]}.\n"
            f"Predictions for the next {periods} hours are: {predictions[sensor_id]}."
        )

    explanation = (
        f"Aggregated insights for machine {machine_id}.\n" +
        "\n".join(explanation_parts)
    )
    
    return MachineInsights(
        machine_id=machine_id,
        explanation=explanation,
        trend=trends,
        seasonal=seasonals,
        anomalies=anomalies,
        predictions=predictions
    )
    
if __name__ == "__main__":
    import uvicorn
    
    anomaly_model, anomaly_scaler = load_anomaly_model()
    prediction_model = load_prediction_model()
    print("Model loaded from blob storage")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)