import time
import asyncio
from datetime import datetime, timedelta
import requests
from azure.cosmos import CosmosClient
from fastapi import BackgroundTasks, FastAPI, HTTPException

app = FastAPI()

# TODO: Make dynamic as per the data from MongoDB

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"
LOG_CONTAINER_NAME = "log-container"
SENSOR_PRED_CONTAINER_NAME = "sensor-predictions"

PREDICTION_URL = "http://localhost:8001/predict_values"
TRAINING_URL = "http://0.0.0.0:8001/train_prediction_model"

# TODO: Make dynamic as per the data from MongoDB
organizations = ["org001", "org002"]
units = ["unt001", "unt002"]
machines = ["mac001", "mac002"]
sensors = ["sen001", "sen002"]

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

def call_training_api(organization_id: str, unit_id:str, machine_id: str, sensor_id: str):
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

    model_type = "prediction"
    log_training_to_cosmos(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type)

async def training_task():
    while True:
        for organization_id in organizations:
            for unit_id in units:
                for machine_id in machines:
                    for sensor_id in sensors:
                        call_training_api(organization_id, unit_id, machine_id, sensor_id)
        
        await asyncio.sleep(86400)  # Sleep for 24 hours

@app.post("/manual_trigger_training")
async def manual_trigger_training(organization_id: str, unit_id:str, machine_id: str, sensor_id: str):
    
    call_training_api(organization_id, unit_id, machine_id, sensor_id)
    return {"detail": "Manual training completed"}

async def execute_api_call(organization_id, unit_id, machine_id, sensor_id, periods, start_timestamp=None):
    api_url = PREDICTION_URL

    payload = {
        "organization_id": organization_id,
        "unit_id": unit_id,
        "machine_id": machine_id,
        "sensor_id": sensor_id,
        "periods": periods
    }

    if start_timestamp:
        payload["start_timestamp"] = start_timestamp

    try:
        response = requests.post(api_url, json=payload)
        response_data = response.json()

        store_prediction_in_cosmos(response_data, periods)

        return response_data
    except Exception as e:
        # print(f"Error during API call: {e}") # As 'NoneType' object is not subscriptable is not error, it is comming as we are returning the null from the API when there is not model related to it
        return

def store_prediction_in_cosmos(data, periods):
    organization_id = data["organization_id"]
    unit_id = data["unit_id"]
    machine_id = data["machine_id"]
    sensor_id = data["sensor_id"]

    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(SENSOR_PRED_CONTAINER_NAME)

    current_time = datetime.now()
    formatted_datetime = current_time.strftime('%Y_%m_%dT%H_%M_%S')

    for i, prediction in enumerate(data["predictions"]):
        prediction_time = current_time + timedelta(hours=i + 1)  # Add prediction for each hour

        log_data = {
            "id": f"{organization_id}_{unit_id}_{machine_id}_{sensor_id}_date_{formatted_datetime}_{i}",
            "organization_id": organization_id,
            "unit_id": unit_id,
            "machine_id": machine_id,
            "sensor_id": sensor_id,
            "prediction_time": prediction_time.isoformat(),
            "prediction_value": prediction,
            "prediction_datetime": current_time.isoformat()
        }

        container.create_item(log_data)

async def schedule_api_calls(periods=24):
    while True:
        for organization_id in organizations:
            for unit_id in units:
                for machine_id in machines:
                    for sensor_id in sensors:
                        await execute_api_call(organization_id, unit_id, machine_id, sensor_id, periods)
        await asyncio.sleep(7200)  # Sleep for 2 hours (7200 seconds)

@app.post("/manual_trigger")
async def manual_trigger(organization_id: str, unit_id:str, machine_id: str, sensor_id: str, periods: int, start_timestamp: str, background_tasks: BackgroundTasks):
    data = await execute_api_call(organization_id, unit_id, machine_id, sensor_id, periods, start_timestamp)
    return data

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(schedule_api_calls())
    asyncio.create_task(training_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)