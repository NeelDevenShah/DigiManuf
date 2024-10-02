import time
import asyncio
from datetime import datetime, timedelta
import requests
import pyodbc
from fastapi import BackgroundTasks, FastAPI, HTTPException

# TODO: Testing
# TODO: Connect DB(sql new one or cosmos or mongo), DB(log of training) and debug
# TODO: Central Server Start, Instead of the different ones from different places

# FastAPI app
app = FastAPI()

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"
LOG_CONTAINER_NAME = "log-container"
SENSOR_PRED_CONTAINER_NAME = "sensor-predictions"

PREDICTION_URL = "http://localhost:8000/predict_values"
TRAINING_URL = "http://0.0.0.0:8000/train_prediction_model"


# Sample dictionary of organizations, machines, sensors
org_data = {
    "org_001": {
        "machines": {
            "mach_001": {
                "sensors": ["sens_001", "sens_002"]
            },
            "mach_002": {
                "sensors": ["sens_003"]
            }
        }
    },
    "org_002": {
        "machines": {
            "mach_003": {
                "sensors": ["sens_004"]
            }
        }
    }
}

###################### Training Code

# Function to log training status to SQL DB
def log_training_to_cosmos(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(LOG_CONTAINER_NAME)

    log_data = {
        "organization_id": organization_id,
        "unit_id": unit_id,
        "machine_id": machine_id,
        "sensor_id": sensor_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "message": message,
        "model_type": model_type
    }

    container.create_item(log_data)

# Function to call the training API and log results
def call_training_api(organization_id: str, unit_id:str, machine_id: str, sensor_id: str):
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
    model_type = "prediction"
    log_training_to_cosmos(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type)

# Function to schedule training every 24 hours for each sensor
async def training_task():
    while True:
        organizations = ["org_001", "org_002"]  # Example organizations, can be dynamically fetched
        for organization_id in organizations:
            units = ["unt_001", "unt_002"]            
            for unit_id in units:
                machines = ["mach_001", "mach_002"]  # Example machines
                for machine_id in machines:
                    sensors = ["sens_001", "sens_002"]  # Example sensors
                    for sensor_id in sensors:
                        # Call training API and log results
                        call_training_api(organization_id, unit_id, machine_id, sensor_id)
        
        await asyncio.sleep(86400)  # Sleep for 24 hours

# Manual training trigger
@app.post("/manual_trigger_training")
async def manual_trigger_training(organization_id: str, unit_id:str, machine_id: str, sensor_id: str):
    # Call training API immediately and log the result
    call_training_api(organization_id, unit_id, machine_id, sensor_id)
    return {"detail": "Manual training completed"}

######################

# Function to call API
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

        # Handle SQL insertion
        store_prediction_in_cosmos(response_data, periods)

        return response_data
    except Exception as e:
        print(f"Error during API call: {e}")
        raise HTTPException(status_code=500, detail="API call failed")

# Function to store predictions in CosmosDB
def store_prediction_in_cosmos(data, periods):
    organization_id = data["organization_id"]
    unit_id = data["unit_id"]
    machine_id = data["machine_id"]
    sensor_id = data["sensor_id"]

    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(LOG_CONTAINER_NAME)

    # Fetch current timestamp
    current_time = datetime.now()

    for i, prediction in enumerate(data["predictions"]):
        prediction_time = current_time + timedelta(hours=i + 1)  # Add prediction for each hour

        log_data = {
            "organization_id": organization_id,
            "unit_id": unit_id,
            "machine_id": machine_id,
            "sensor_id": sensor_id,
            "prediction_time": prediction_time,
            "prediction_value": prediction,
            "prediction_datetime": current_time
        }

        container.create_item(log_data)

# Schedule task for every 2 hours
async def schedule_api_calls(periods=24):
    while True:
        for org_id, org_info in org_data.items():
            for mach_id, mach_info in org_info["machines"].items():
                for sensor_id in mach_info["sensors"]:
                    # Call API for each sensor
                    await execute_api_call(org_id, mach_id, sensor_id, periods)
        await asyncio.sleep(7200)  # Sleep for 2 hours (7200 seconds)

# API endpoint for manual trigger
@app.post("/manual_trigger")
async def manual_trigger(organization_id: str, unit_id:str, machine_id: str, sensor_id: str, periods: int, start_timestamp: str, background_tasks: BackgroundTasks):
    # Manually trigger API call
    data = await execute_api_call(organization_id, unit_id, machine_id, sensor_id, periods, start_timestamp)
    return data

# Run API calls in background
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(schedule_api_calls())
    asyncio.create_task(training_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)