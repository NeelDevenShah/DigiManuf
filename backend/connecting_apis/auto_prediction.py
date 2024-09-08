import time
import asyncio
from datetime import datetime, timedelta
import requests
import pyodbc
from fastapi import BackgroundTasks, FastAPI, HTTPException

# FastAPI app
app = FastAPI()

# TODO: Connect DB and debug
# Schema of the sql database for output storage

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

# Azure SQL Configuration
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=<server_name>;DATABASE=<database_name>;UID=<user>;PWD=<password>')
cursor = conn.cursor()

# Function to call API
async def execute_api_call(organization_id, machine_id, sensor_id, periods, start_timestamp=None):
    api_url = "http://localhost:8000/predict_values"

    payload = {
        "organization_id": organization_id,
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
        store_prediction_in_azure_sql(response_data, periods)

        return response_data
    except Exception as e:
        print(f"Error during API call: {e}")
        raise HTTPException(status_code=500, detail="API call failed")

# Function to store predictions in Azure SQL
def store_prediction_in_azure_sql(data, periods):
    organization_id = data["organization_id"]
    machine_id = data["machine_id"]
    sensor_id = data["sensor_id"]

    # Fetch current timestamp
    current_time = datetime.now()

    for i, prediction in enumerate(data["predictions"]):
        prediction_time = current_time + timedelta(hours=i + 1)  # Add prediction for each hour

        cursor.execute("""
            INSERT INTO sensor_predictions 
            (organization_id, machine_id, sensor_id, prediction_time, prediction_value, prediction_datetime)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (organization_id, machine_id, sensor_id, prediction_time, prediction, current_time))

    conn.commit()

# Schedule task for every 2 hours
async def schedule_api_calls(periods=5):
    while True:
        for org_id, org_info in org_data.items():
            for mach_id, mach_info in org_info["machines"].items():
                for sensor_id in mach_info["sensors"]:
                    # Call API for each sensor
                    await execute_api_call(org_id, mach_id, sensor_id, periods)
        await asyncio.sleep(7200)  # Sleep for 2 hours (7200 seconds)

# API endpoint for manual trigger
@app.post("/manual_trigger")
async def manual_trigger(organization_id: str, machine_id: str, sensor_id: str, periods: int, start_timestamp: str, background_tasks: BackgroundTasks):
    # Manually trigger API call
    data = await execute_api_call(organization_id, machine_id, sensor_id, periods, start_timestamp)
    return data

# Run API calls in background
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(schedule_api_calls())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)