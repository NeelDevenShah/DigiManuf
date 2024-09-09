import asyncio
from datetime import datetime, timedelta
import requests
import pandas as pd
from azure.cosmos import CosmosClient
from fastapi import BackgroundTasks, FastAPI, HTTPException

# FastAPI app
app = FastAPI()

# CosmosDB config
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

# TODO: Connect DB(auth one) and DB(timedate cosmos), DB (log of training) and debug

# TODO: Schema of the sql database for training log
# CREATE TABLE model_training_log (
#     id SERIAL PRIMARY KEY,
#     organization_id VARCHAR(255) NOT NULL,
#     machine_id VARCHAR(255) NOT NULL,
#     sensor_id VARCHAR(255) NOT NULL,
#     start_time TIMESTAMP NOT NULL,
#     end_time TIMESTAMP,
#     status VARCHAR(100) DEFAULT 'PENDING',
#     message VARCHAR(100),
#     model_type VARCHAR(30),
# );

# The value of the anomaly is itself stored in the azure cosmos database, by increasing the one key value pair.

ANOMALY_URL = "http://0.0.0.0:8000/predict_anomaly"
TRAINING_URL = "http://0.0.0.0:8000/train_anomaly_model"

#####################
    # Training Code

# SQL DB connection config for logging training data
SQL_SERVER = "your_sql_server.database.windows.net"
SQL_DATABASE = "your_database"
SQL_USERNAME = "your_username"
SQL_PASSWORD = "your_password"
SQL_DRIVER = "{ODBC Driver 17 for SQL Server}"

# Function to log training status to SQL DB
def log_training_to_sql(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type):
    conn_str = f"DRIVER={SQL_DRIVER};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO training_logs (organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type))
    
    conn.commit()
    cursor.close()
    conn.close()

# Function to call the training API and log results
def call_training_api(organization_id: str, machine_id: str, sensor_id: str):
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
    log_training_to_sql(organization_id, unit_id, machine_id, sensor_id, start_time, end_time, status, message, model_type)

# Function to schedule training every 24 hours for each sensor
async def training_task():
    while True:
        organizations = ["org_001", "org_002"]  # Example organizations, can be dynamically fetched
        for organization_id in organizations:
            machines = ["mach_001", "mach_002"]  # Example machines
            for machine_id in machines:
                sensors = ["sens_001", "sens_002"]  # Example sensors
                for sensor_id in sensors:
                    # Call training API and log results
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
def fetch_data_from_cosmos(organization_id: str, unit_id: str, achine_id: str, sensor_id: str):
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
            units = ["unt_001", "unt_002"]  # You can modify or dynamically fetch organizations
            for unit_id in units:
                # Iterate over machines and sensors (similar to org_data in previous examples)
                machines = ["mach_001", "mach_002"]  # Example machines
                for machine_id in machines:
                    sensors = ["sens_001", "sens_002"]  # Example sensors
                    for sensor_id in sensors:
                        # Fetch data from CosmosDB for each sensor
                        df = fetch_data_from_cosmos(organization_id, unit_id, machine_id, sensor_id)
                        if not df.empty:
                            # Process anomaly detection and update DB
                            process_anomaly_detection(df)
        await asyncio.sleep(300)  # Run every 5 minutes

# Manual trigger for immediate anomaly detection
@app.post("/manual_trigger_anomaly")
async def manual_trigger_anomaly(organization_id: str, unit_id: str, machine_id: str, sensor_id: str, background_tasks: BackgroundTasks):
    df = fetch_data_from_cosmos(organization_id, unit_id, machine_id, sensor_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the given parameters")
    
    # Process anomaly detection synchronously (wait for output)
    process_anomaly_detection(df)
    return {"detail": "Manual anomaly detection completed"}

# Background task startup
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(anomaly_detection_task())
    asyncio.create_task(training_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
