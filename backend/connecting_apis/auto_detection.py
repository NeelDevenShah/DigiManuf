import asyncio
from datetime import datetime, timedelta
import requests
import pandas as pd
from azure.cosmos import CosmosClient
from fastapi import BackgroundTasks, FastAPI, HTTPException

# TODO: Testing
# TODO: Connect DB(auth one) and DB(timedate cosmos), DB (log of training) and debug
# TODO: Central Server Start, Instead of the different ones from different places

# FastAPI app
app = FastAPI()

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"
LOG_CONTAINER_NAME = "log-container"

# INFO: The value of the anomaly is itself stored in the azure cosmos database, by increasing the one key value pair.

ANOMALY_URL = "http://0.0.0.0:8000/predict_anomaly"
TRAINING_URL = "http://0.0.0.0:8000/train_anomaly_model"

# TODO: Make dynamic as per the data from MongoDB
organizations = ["org_001"]  # You can modify or dynamically fetch organizations
units = ["unt_001"]  # You can modify or dynamically fetch organizations
machines = ["mach_001"]  # Example machines
sensors = ["sens_001"]  # Example sensors

###################### Training Code

# Function to log training status to CosmosDB
def log_training_to_cosmos(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(LOG_CONTAINER_NAME)
    
    datetime_obj = datetime.now()
    formatted_datetime = datetime_obj.strftime('%Y_%m_%dT%H_%M_%S')
    log_data = {
        "id": f"{organization_id}_{unit_id}_{machine_id}_{sensor_id}_date_{formatted_datetime}",
        "organization_id": organization_id,
        "unit_id": unit_id,
        "machine_id": machine_id,
        "sensor_id": sensor_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": status,
        "message": message,
        "model_type": model_type
    }

    container.create_item(log_data)

# Function to call the training API and log results
def call_training_api(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    payload = {
        "organization_id": organization_id,
        "unit_id": unit_id,
        "machine_id": machine_id,
        "sensor_id": sensor_id
    }

    start_time = datetime.now()

    try:
        # Call the training API
        response = requests.post(TRAINING_URL, json=payload)

        # Check the response status
        if response.status_code == 200:
            status = "success"
            message = "Training completed successfully"
        else:
            status = "failure"
            message = f"Failed to train model: {response.content}"

    except Exception as e:
        status = "failure"
        message = str(e)

    end_time = datetime.now()

    # Log training details to SQL
    model_type = "anomaly"
    log_training_to_cosmos(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type)

# Function to schedule training every 24 hours for each sensor
async def training_task():
    while True:
        for organization_id in organizations:
            for unit_id in units:
                for machine_id in machines:
                    for sensor_id in sensors:
                        call_training_api(organization_id, unit_id, machine_id, sensor_id)
        
        await asyncio.sleep(86400)  # Sleep for 24 hours

# Manual training trigger
@app.post("/manual_trigger_training")
async def manual_trigger_training(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    # Call training API immediately and log the result
    call_training_api(organization_id, unit_id, machine_id, sensor_id)
    return {"detail": "Manual training completed"}

######################

# Function to fetch data from CosmosDB (last 10 minutes)
def fetch_data_from_cosmos(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Calculate time 10 minutes ago
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    ten_minutes_ago_str = ten_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')

    # Query data from last 10 minutes
    query = f"""SELECT * FROM c 
                WHERE c.organization_id = '{organization_id}' 
                AND c.unit_id = '{unit_id}' 
                AND c.machine_id = '{machine_id}' 
                AND c.sensor_id = '{sensor_id}' 
                AND c.datetime >= '{ten_minutes_ago_str}'"""
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from the last 10 minutes for {organization_id}, {machine_id}, {sensor_id}")
    return df

# Function to call anomaly detection API
def call_anomaly_api(data):
    api_url = ANOMALY_URL
    
    payload = {
        "organization_id": data["organization_id"],
        "unit_id": data["unit_id"],
        "machine_id": data["machine_id"],
        "sensor_id": data["sensor_id"],
        "datetime": data["datetime"],
        "temperature": data["temperature"],
        "second": data["second"],
        "minute": data["minute"],
        "hour": data["hour"],
        "day": data["day"],
        "month": data["month"],
        "year": data["year"],
        "day_of_week": data["day_of_week"],
        "is_weekend": data["is_weekend"],
        "rolling_mean_temp": data["rolling_mean_temp"],
        "rolling_std_temp": data["rolling_std_temp"],
        "temp_lag_1s": data["temp_lag_1s"]
    }

    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: Anomaly API call failed")

# Function to update data in CosmosDB with anomaly prediction
def update_cosmos_with_anomaly_prediction(data, is_anomaly):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # Add anomaly prediction to the existing document
    data["anomaly_model_prediction"] = is_anomaly

    # Replace the document with updated data
    container.upsert_item(data)

# Function to execute anomaly detection for each fetched record
def process_anomaly_detection(df):
    for _, row in df.iterrows():
        # Call anomaly API for each record
        anomaly_response = call_anomaly_api(row)
        is_anomaly = anomaly_response.get("is_anomaly", False)

        update_cosmos_with_anomaly_prediction(row.to_dict(), is_anomaly)

# Scheduled task to check for anomalies every 5 minutes
async def anomaly_detection_task():
    while True:
        for organization_id in organizations:
            for unit_id in units:
                for machine_id in machines:
                    for sensor_id in sensors:
                        df = fetch_data_from_cosmos(organization_id, unit_id, machine_id, sensor_id)
                        if not df.empty:
                            process_anomaly_detection(df)
        await asyncio.sleep(300)  # Run every 5 minutes

# Manual trigger for immediate anomaly detection
@app.post("/manual_trigger_anomaly")
async def manual_trigger_anomaly(organization_id: str, unit_id: str, machine_id: str, sensor_id: str, background_tasks: BackgroundTasks):
    df = fetch_data_from_cosmos(organization_id, unit_id, machine_id, sensor_id)

    if not df.empty:
        process_anomaly_detection(df)
    return {"detail": "Manual anomaly detection completed"}

# Background task startup
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(anomaly_detection_task())
    asyncio.create_task(training_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
