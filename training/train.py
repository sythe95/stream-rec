import os
import pandas as pd
from dotenv import load_dotenv
import mlflow
import mlflow.sklearn
from feast import FeatureStore
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import boto3
from botocore.client import Config

# ==========================================
# 1. SMART CONFIGURATION (Docker vs Windows)
# ==========================================
load_dotenv()

# AWS / MinIO Standard Settings
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_S3_ADDRESSING_STYLE"] = "path"
os.environ["MLFLOW_S3_IGNORE_TLS"] = "true"
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

# -------------------------------------------------------------------------
# DYNAMIC ENDPOINTS:
# - If running in Docker, these ENV VARS will be set (pointing to 'minio:9000' and 'mlflow:5000')
# - If running on Windows, we default to 'localhost' ports (9010 and 5000)
# -------------------------------------------------------------------------

# 1. MinIO Endpoint
# Internal Docker: http://minio:9000
# External Windows: http://localhost:9010
minio_endpoint = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://localhost:9010")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = minio_endpoint

# 2. MLflow Tracking URI
# Internal Docker: http://mlflow:5000
# External Windows: http://localhost:5000
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(tracking_uri)

EXPERIMENT_NAME = "stream-rec-final"
mlflow.set_experiment(EXPERIMENT_NAME)

print(f"🚀 Starting Training Pipeline")
print(f"   > Environment: {'Docker' if 'mlflow' in tracking_uri else 'Windows'}")
print(f"   > MLflow URI:  {tracking_uri}")
print(f"   > MinIO URL:   {minio_endpoint}")

# ==========================================
# 2. BUCKET SETUP
# ==========================================
def ensure_bucket_exists(bucket_name):
    """
    Ensures the S3 bucket exists using a direct Boto3 connection.
    """
    print(f"🔍 Checking bucket '{bucket_name}'...")
    
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    s3 = boto3.client(
        "s3",
        endpoint_url=minio_endpoint, # Use the dynamic endpoint
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4')
    )
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"   ✅ Bucket '{bucket_name}' created/verified.")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"   ✅ Bucket '{bucket_name}' already exists.")
    except Exception as e:
        print(f"   ⚠️ Warning: Could not verify bucket. Error: {e}")

bucket_name = os.getenv("MINIO_BUCKET_NAME", "stream-rec")
ensure_bucket_exists(bucket_name)

# ==========================================
# 3. GENERATE OFFLINE DATA & FETCH (FEAST)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))

if os.path.exists("/app/feature_repo"):
    repo_path = "/app/feature_repo"
else:
    repo_path = os.path.join(current_dir, "..", "feature_repo")

# --- THE FIX: Force-generate the Parquet file so Dask has a valid table to join ---
data_dir = os.path.join(repo_path, "data")
os.makedirs(data_dir, exist_ok=True)
parquet_path = os.path.join(data_dir, "user_stats.parquet")

print(f"\n📁 Verifying offline feature data at: {parquet_path}")
# Create historical features from exactly 1 day ago
historical_data = pd.DataFrame({
    "user_id": pd.Series([1, 2, 3, 4, 5], dtype="int64"),
    "event_timestamp": pd.to_datetime([pd.Timestamp.now() - pd.Timedelta(days=1)] * 5), 
    "total_ratings": pd.Series([10, 25, 5, 100, 42], dtype="int64"),
    "avg_rating": pd.Series([4.5, 3.8, 2.1, 4.9, 3.9], dtype="float32")
})
historical_data.to_parquet(parquet_path)
print("   ✅ Offline Parquet file generated.")

store = FeatureStore(repo_path=repo_path)

print("\n📊 Fetching historical features from Feast...")
# Entity timestamps must be from NOW so the PIT join looks backward and finds yesterday's features
entity_df = pd.DataFrame({
    "user_id": pd.Series([1, 2, 3, 4, 5], dtype="int64"),
    "event_timestamp": pd.to_datetime([pd.Timestamp.now()] * 5), 
    "target_next_rating": pd.Series([4.8, 3.5, 2.0, 4.9, 4.0], dtype="float64") 
})

try:
    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "user_stats:total_ratings",
            "user_stats:avg_rating",
        ]
    ).to_df()

    # Clean data
    training_df = training_df.drop(columns=["event_timestamp"])
    training_df.fillna(0, inplace=True) 
    print(f"   ✅ Data loaded. Shape: {training_df.shape}")

    # ==========================================
    # 4. TRAIN MODEL
    # ==========================================
    print("\n🧠 Training model...")
    X = training_df[["total_ratings", "avg_rating"]]
    y = training_df["target_next_rating"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run():
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f"   📉 Mean Squared Error: {mse}")
        
        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_metric("mse", mse)
        
        print("📤 Uploading model artifact to MinIO...")
        mlflow.sklearn.log_model(
            sk_model=model, 
            artifact_path="recommender_model"
        )
        
        print("📝 Registering model in MLflow Registry...")
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/recommender_model"
        mlflow.register_model(model_uri=model_uri, name="rec_model_v1")
        
        print("\n✨ SUCCESS! Model saved and registered to MLflow.")

except Exception as e:
    print(f"\n❌ Error during training/feature retrieval: {e}")