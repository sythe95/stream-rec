from datetime import timedelta
from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    FileSource,
    PushSource,
    RequestSource,
)
from feast.types import Float32, Int64, String
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "..", "data", "user_stats.parquet")
# 1. Define the Entity (The "Primary Key")
# In our case, everything revolves around a User ID.
user = Entity(name="user", join_keys=["user_id"])

# 2. Define the Data Source (Offline)
# We will put a parquet file here in the next step.
user_stats_source = FileSource(
    name="user_stats_source",
    path=data_path,
    timestamp_field="event_timestamp",
)

# 3. Define the Feature View
# This groups features together (like columns in a table).
user_stats_view = FeatureView(
    name="user_stats",
    entities=[user],
    ttl=timedelta(days=36500), # Keep data "fresh" for a long time for this demo
    schema=[
        Field(name="total_ratings", dtype=Int64),
        Field(name="avg_rating", dtype=Float32),
        Field(name="favorite_genre", dtype=String),
    ],
    online=True, # Allow this to be synced to Redis
    source=user_stats_source,
)

# 4. Define a Feature Service
# This is what our API will ask for: "Give me the user_activity_v1 service"
user_service = FeatureService(
    name="user_activity_v1",
    features=[user_stats_view],
)