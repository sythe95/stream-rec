from datetime import timedelta
from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    FileSource,
    PushSource,
    ValueType,
)
from feast.types import Float32, Int64

# 1. Define the Entity (the primary key for our features)
user = Entity(
    name="user", 
    join_keys=["user_id"], 
    value_type=ValueType.INT64
)

# 2. Define the Batch Source (Historical data for DuckDB to train on)
# We use the absolute path so DuckDB never gets lost inside the Docker container
user_stats_batch_source = FileSource(
    name="user_stats_source",
    path="/app/feature_repo/data/user_stats.parquet",
    timestamp_field="event_timestamp",
)

# 3. Define the Stream Source
rating_push_source = PushSource(
    name="rating_push_source",
    batch_source=user_stats_batch_source
)

# 4. Define the Feature View
user_stats_fv = FeatureView(
    name="user_stats",
    entities=[user],
    ttl=timedelta(days=365),
    schema=[
        Field(name="avg_rating", dtype=Float32),
        Field(name="total_ratings", dtype=Int64),
    ],
    source=rating_push_source,  # <--- FIXED: Just pass the PushSource here!
)

# 5. Define the Feature Service
user_stats_fs = FeatureService(
    name="user_stats_service",
    features=[user_stats_fv]
)