import asyncio
from datetime import datetime, timedelta
import requests
import pandas as pd
from azure.cosmos import CosmosClient
from fastapi import BackgroundTasks, FastAPI, HTTPException

# FastAPI app
app = FastAPI()

# TODO: Connect DB(auth one) and DB(timedate cosmos) and debug

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

# Function to fetch data from CosmosDB (last 10 minutes)
def fetch_data_from_cosmos(organization_id: str, machine_id: str, sensor_id: str):
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Calculate time 10 minutes ago
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    ten_minutes_ago_str = ten_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')

    # Query data from last 10 minutes
    query = f"""SELECT * FROM c 
                WHERE c.organization_id = '{organization_id}' 
                AND c.machine_id = '{machine_id}' 
                AND c.sensor_id = '{sensor_id}' 
                AND c.datetime >= '{ten_minutes_ago_str}'"""
    
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    df = pd.DataFrame(items)
    print(f"Fetched {len(df)} records from the last 10 minutes for {organization_id}, {machine_id}, {sensor_id}")
    return df

# Function to call anomaly detection API
def call_anomaly_api(data):
    api_url = "http://0.0.0.0:8000/predict_anomaly"
    
    payload = {
        "organization_id": data["organization_id"],
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
        raise HTTPException(status_code=500, detail="Anomaly API call failed")

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

        # Update Cosmos DB with the anomaly prediction
        update_cosmos_with_anomaly_prediction(row.to_dict(), is_anomaly)

# Scheduled task to check for anomalies every 5 minutes
async def anomaly_detection_task():
    while True:
        # TODO: Dynamic data from the Database different then that of timeseries database, Second one from where auth is controlled 
        
        organizations = ["org_001", "org_002"]  # You can modify or dynamically fetch organizations
        for organization_id in organizations:
            # Iterate over machines and sensors (similar to org_data in previous examples)
            machines = ["mach_001", "mach_002"]  # Example machines
            for machine_id in machines:
                sensors = ["sens_001", "sens_002"]  # Example sensors
                for sensor_id in sensors:
                    # Fetch data from CosmosDB for each sensor
                    df = fetch_data_from_cosmos(organization_id, machine_id, sensor_id)
                    if not df.empty:
                        # Process anomaly detection and update DB
                        process_anomaly_detection(df)
        await asyncio.sleep(300)  # Run every 5 minutes

# Manual trigger for immediate anomaly detection
@app.post("/manual_trigger_anomaly")
async def manual_trigger_anomaly(organization_id: str, machine_id: str, sensor_id: str, background_tasks: BackgroundTasks):
    df = fetch_data_from_cosmos(organization_id, machine_id, sensor_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the given parameters")
    
    # Process anomaly detection synchronously (wait for output)
    process_anomaly_detection(df)
    return {"detail": "Manual anomaly detection completed"}

# Background task startup
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(anomaly_detection_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
