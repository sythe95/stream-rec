from feast import FeatureStore
import pandas as pd

# 1. Initialize the Store
store = FeatureStore(repo_path="feature_repo")

# 2. Define who we want to query
# We want features for User ID 1
entity_rows = [
    {"user_id": 1}
]

# 3. Fetch from the Online Store (Redis)
print("⏳ Fetching features from Redis...")
feature_vector = store.get_online_features(
    features=[
        "user_stats:total_ratings",
        "user_stats:avg_rating",
        "user_stats:favorite_genre"
    ],
    entity_rows=entity_rows
).to_dict()

# 4. Print the result
print("\n🎉 SUCCESS! Retrieved Feature Vector:")
print(feature_vector)

# Validation check
if feature_vector["user_id"][0] == 1:
    print("\n✅ User ID matches.")
else:
    print("\n❌ User ID mismatch.")