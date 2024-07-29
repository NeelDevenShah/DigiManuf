import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="eventhubname",
                               connection="newhubneel_events_IOTHUB") 
def eventhub_trigger1(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s', azeventhub.get_body().decode('utf-8'))
    try:
        message_data = json.loads(azeventhub.get_body().decode('utf-8'))
        logging.info('Message extracted: %s', message_data)

        # Extract values from the dictionary
        device_id = message_data.get('deviceId')
        temperature = message_data.get('temperature')
        humidity = message_data.get('humidity')
        timestamp = message_data.get('timestamp')

        # Log the extracted values
        logging.info('Device ID: %s', device_id)
        logging.info('Temperature: %s', temperature)
        logging.info('Humidity: %s', humidity)
        logging.info('Timestamp: %s', timestamp)

    except Exception as e:
        logging.error('Error processing the event: %s', str(e))
