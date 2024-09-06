from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Initialize the Cosmos client
COSMOS_DB_ENDPOINT = ""
COSMOS_DB_KEY = ""
DATABASE_NAME = ""
CONTAINER_NAME = ""

# Create a Cosmos client
client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)

# Create or get the database
database = client.get_database_client(DATABASE_NAME)

# Create or get the container
container = database.get_container_client(CONTAINER_NAME)

# Query to get all documents
query = "SELECT * FROM c"

try:
    # Fetch all documents
    items = container.query_items(query=query, enable_cross_partition_query=True)

    # Iterate over documents and delete each one
    for item in items:
        # Extract the id and partition key
        item_id = item['id']
        partition_key_value = item['id']
        # Delete the document
        container.delete_item(item_id, partition_key_value)
        print(f"Deleted document with id: {item_id}")

except exceptions.CosmosHttpResponseError as e:
    print(f"An error occurred: {e.message}")
