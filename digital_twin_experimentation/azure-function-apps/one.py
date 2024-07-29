import azure.functions as func
import logging

app = func.FunctionApp()

# Here, make the connection named newhubneel_events_IOTHUB in the azure funcitons -> environment variables -> App Settings -> Add
@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="eventhubname",
                               connection="newhubneel_events_IOTHUB") 
def eventhub_trigger1(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                azeventhub.get_body().decode('utf-8'))
