import os
import pandas as pd
import warnings
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp, avg, count
from pyspark.sql.types import StructType, StructField, LongType, FloatType

# Mute warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("root").setLevel(logging.ERROR)

print("🔥 Booting Apache Spark...")
spark = SparkSession.builder \
    .appName("StreamRecProcessor") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

from feast import FeatureStore
store = FeatureStore(repo_path="/app/feature_repo")

# ==========================================
# 1. MATCH THE SIMULATOR'S RAW SCHEMA
# ==========================================
input_schema = StructType([
    StructField("user_id", LongType(), True),
    StructField("movie_id", LongType(), True),
    StructField("rating", FloatType(), True),
    StructField("timestamp", LongType(), True)
])

print("📡 Connecting to Redpanda stream...")
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "redpanda:29092") \
    .option("subscribe", "user_ratings") \
    .option("startingOffsets", "latest") \
    .load()

parsed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), input_schema).alias("data")) \
    .select("data.*")

# ==========================================
# 2. REAL-TIME STREAMING AGGREGATION
# ==========================================
# Group by user_id and calculate running average and count on the fly
aggregated_df = parsed_df \
    .groupBy("user_id") \
    .agg(
        avg("rating").alias("avg_rating"),
        count("rating").alias("total_ratings")
    ) \
    .withColumn("event_timestamp", current_timestamp())

# ==========================================
# 3. PUSH TO FEAST
# ==========================================
def push_to_feast(batch_df, batch_id):
    pandas_df = batch_df.toPandas()
    
    if not pandas_df.empty:
        pandas_df["event_timestamp"] = pd.to_datetime(pandas_df["event_timestamp"], utc=True)
        # Ensure total_ratings stays an integer
        pandas_df["total_ratings"] = pandas_df["total_ratings"].astype("int64")
        
        print(f"\n📦 Batch {batch_id} | Updating Feast Redis Cache:")
        # Print the actual math Spark just did so we can see it!
        print(pandas_df[["user_id", "avg_rating", "total_ratings"]].to_string(index=False))
        
        store.push("rating_push_source", pandas_df)

print("🚀 Starting PySpark Stateful Aggregation...")
# Notice outputMode is "update" - it only outputs users whose ratings changed in this batch!
query = aggregated_df.writeStream \
    .outputMode("update") \
    .foreachBatch(push_to_feast) \
    .start()

query.awaitTermination()