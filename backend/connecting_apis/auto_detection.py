# Micro-service-1

import asyncio
from datetime import datetime, timedelta
import requests
import pandas as pd
from azure.cosmos import CosmosClient
from pymongo import MongoClient
from bson import ObjectId
from fastapi import BackgroundTasks, FastAPI, HTTPException

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

# Mongo Configuations
client = MongoClient("")
db = client['digimanuf']

async def get_sensor_data():
    try:
        sensors = db.sensors.find()
        unique_data = set()

        for sensor in list(sensors):
            sensor_tuple = (str(sensor.get('organization')), 
                            str(sensor.get('unit')), 
                            str(sensor.get('machine')), 
                            str(sensor.get('_id')))

            unique_data.add(sensor_tuple)

        unique_data_list = list(unique_data)
        
        return unique_data_list

    except Exception as e:
        print(f"Error: {e}")
        return

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

def call_training_api(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    payload = {
        "organization_id": organization_id,
        "unit_id": unit_id,
        "machine_id": machine_id,
        "sensor_id": sensor_id
    }

    start_time = datetime.now()

    try:
        response = requests.post(TRAINING_URL, json=payload)

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

    model_type = "anomaly"
    log_training_to_cosmos(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type)

async def training_task():
    while True:
        sensor_data = await get_sensor_data()
        for organization_id, unit_id, machine_id, sensor_id in sensor_data:
            call_training_api(organization_id, unit_id, machine_id, sensor_id)
        
        await asyncio.sleep(86400)  # Sleep for 24 hours

@app.post("/manual_trigger_training")
async def manual_trigger_training(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):

    call_training_api(organization_id, unit_id, machine_id, sensor_id)
    return {"detail": "Manual training completed"}

def fetch_data_from_cosmos(organization_id: str, unit_id: str, machine_id: str, sensor_id: str):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Calculate time 10 minutes ago
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    ten_minutes_ago_str = ten_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')

    query = f"""SELECT * FROM c 
                WHERE c.organization_id = '{organization_id}' 
                AND c.unit_id = '{unit_id}' 
                AND c.machine_id = '{machine_id}' 
                AND c.sensor_id = '{sensor_id}' 
                AND c.datetime >= '{ten_minutes_ago_str}'"""
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from the last 10 minutes for {organization_id}, {unit_id}, {machine_id}, {sensor_id}")
    return df

def call_anomaly_api(data):
    try:
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
    except:
        # print(f"Error during API call: {e}") # As 'NoneType' object is not subscriptable is not error, it is comming as we are returning the null from the API when there is not model related to it
        return

def update_cosmos_with_anomaly_prediction(data, is_anomaly):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    data["anomaly_model_prediction"] = is_anomaly

    container.upsert_item(data)

def process_anomaly_detection(df):
    for _, row in df.iterrows():
        try:
            anomaly_response = call_anomaly_api(row)
            # print(anomaly_response)
            is_anomaly = anomaly_response.get("is_anomaly", False)

            update_cosmos_with_anomaly_prediction(row.to_dict(), is_anomaly)
        except:
            print("Error: Anomaly API call failed")

async def anomaly_detection_task():
    while True:
        sensor_data = await get_sensor_data()
        for organization_id, unit_id, machine_id, sensor_id in sensor_data:
            df = fetch_data_from_cosmos(organization_id, unit_id, machine_id, sensor_id)
            if not df.empty:
                process_anomaly_detection(df)
                        
        await asyncio.sleep(300)  # Run every 5 minutes

@app.post("/manual_trigger_anomaly")
async def manual_trigger_anomaly(organization_id: str, unit_id: str, machine_id: str, sensor_id: str, background_tasks: BackgroundTasks):
    df = fetch_data_from_cosmos(organization_id, unit_id, machine_id, sensor_id)

    if not df.empty:
        process_anomaly_detection(df)
    return {"detail": "Manual anomaly detection completed"}

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(anomaly_detection_task())
    asyncio.create_task(training_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)