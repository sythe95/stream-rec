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
data_path = os.path.join(current_dir, "data", "user_stats.parquet")

# 1. Define the Entity (The "Primary Key")
user = Entity(name="user", join_keys=["user_id"])

# 2. Define the Data Source (Offline)
user_stats_source = FileSource(
    name="user_stats_source",
    path=data_path,
    timestamp_field="event_timestamp",
)

# --- ADDED: Define the Streaming Push Source (The Trapdoor) ---
rating_push_source = PushSource(
    name="rating_push_source",
    batch_source=user_stats_source,
)
# --------------------------------------------------------------

# 3. Define the Feature View
user_stats_view = FeatureView(
    name="user_stats",
    entities=[user],
    ttl=timedelta(days=36500), 
    schema=[
        Field(name="total_ratings", dtype=Int64),
        Field(name="avg_rating", dtype=Float32),
        Field(name="favorite_genre", dtype=String),
    ],
    online=True, 
    source=rating_push_source, # <--- The trapdoor is now the MAIN source!
)

# 4. Define a Feature Service
user_service = FeatureService(
    name="user_activity_v1",
    features=[user_stats_view],
)