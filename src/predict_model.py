import os
import pandas as pd
import mlflow.pyfunc
from feast import FeatureStore
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. CONFIGURATION
load_dotenv()
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MINIO_ENDPOINT = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://127.0.0.1:9010")

# Fix Connection Settings
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_S3_ADDRESSING_STYLE"] = "path"
os.environ["MLFLOW_S3_IGNORE_TLS"] = "true"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = MINIO_ENDPOINT

app = FastAPI(title="StreamRec Inference API")

# 2. LOAD RESOURCES
print("🚀 Connecting to Feature Store...")
# This now connects to Redis (via the env var in docker-compose)
store = FeatureStore(repo_path="feature_repo")

print(f"🚀 Connecting to MLflow ({TRACKING_URI})...")
mlflow.set_tracking_uri(TRACKING_URI)

model_name = "rec_model_v1"
model_version = "1"
model_uri = f"models:/{model_name}/{model_version}"
loaded_model = None

try:
    loaded_model = mlflow.pyfunc.load_model(model_uri)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")

# 3. ENDPOINTS
class PredictionRequest(BaseModel):
    user_id: int

@app.post("/predict")
def predict(request: PredictionRequest):
    if not loaded_model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        print(f"🔮 Fetching Online Features for User ID: {request.user_id}")
        
        # 1. Get features from Redis
        feature_vector = store.get_online_features(
            features=[
                "user_stats:total_ratings",
                "user_stats:avg_rating"
            ],
            entity_rows=[{"user_id": request.user_id}]
        ).to_dict()
        
        features_df = pd.DataFrame.from_dict(feature_vector)
        
        # 2. Check if user exists
        if features_df["total_ratings"].iloc[0] is None:
            return {"status": "error", "message": "User not found in Feature Store (Redis)"}

        # 3. Clean Data (Drop ID column so it matches training shape)
        model_input = features_df.drop(columns=["user_id"])

        # 4. Predict
        prediction = loaded_model.predict(model_input)
        result = float(prediction[0])
        
        return {
            "user_id": request.user_id,
            "features_fetched": feature_vector,
            "predicted_rating": round(result, 2),
            "status": "success"
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))