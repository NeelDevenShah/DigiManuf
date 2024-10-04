from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Initialize the Cosmos client
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = "sensor_data"
CONTAINER_NAME = "dm-1"

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)
query = "SELECT * FROM c"

try:
    items = container.query_items(query=query, enable_cross_partition_query=True)

    for item in items:
        item_id = item['id']
        partition_key_value = item['id']
        container.delete_item(item_id, partition_key_value)
        print(f"Deleted document with id: {item_id}")

except exceptions.CosmosHttpResponseError as e:
    print(f"An error occurred: {e.message}")
