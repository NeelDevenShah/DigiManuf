from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

# Initialize Spark session
spark = SparkSession.builder.appName("SensorDataTraining").getOrCreate()

# Define Azure Storage account details
storage_account_name = "YourStorageAccountName"
storage_account_access_key = "YourStorageAccountAccessKey"
container_name = "sensor-data"

# Set up configuration
spark.conf.set(f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net", storage_account_access_key)

# Load data from Azure Blob Storage
data_path = f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/*"
raw_data = spark.read.json(data_path)

# Preprocess data
data = raw_data.select(col("temperature").cast("double"), col("humidity").cast("double"))

# Assemble features
assembler = VectorAssembler(inputCols=["temperature"], outputCol="features")
data = assembler.transform(data)

# Split data into training and test sets
train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

# Train a linear regression model
lr = LinearRegression(featuresCol="features", labelCol="humidity")
lr_model = lr.fit(train_data)

# Evaluate the model
predictions = lr_model.transform(test_data)
evaluator = RegressionEvaluator(labelCol="humidity", predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print(f"Root Mean Squared Error (RMSE) on test data = {rmse}")

# Save the trained model
model_path = f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/models/sensor_model"
lr_model.save(model_path)

