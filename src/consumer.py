import json
import uuid
import pandas as pd
from kafka import KafkaConsumer
from feast import FeatureStore

print("🔄 Initializing Feast Feature Store...")
store = FeatureStore(repo_path="/app/feature_repo")

# ADDED: favorite_genre to the mock state
mock_redis_state = {
    1: {"total_ratings": 55, "avg_rating": 4.6, "favorite_genre": "Sci-Fi"},
    2: {"total_ratings": 10, "avg_rating": 3.0, "favorite_genre": "Comedy"},
    3: {"total_ratings": 100, "avg_rating": 4.1, "favorite_genre": "Action"},
    4: {"total_ratings": 5, "avg_rating": 2.5, "favorite_genre": "Horror"},
    5: {"total_ratings": 20, "avg_rating": 3.8, "favorite_genre": "Drama"}
}

print("🔄 Connecting to Redpanda...")
consumer = KafkaConsumer(
    bootstrap_servers=['redpanda:29092'],
    group_id=f"stream_rec_processor_{uuid.uuid4()}",
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

consumer.subscribe(['user_ratings'])
print("🎧 Stream Processor Live! Pushing to Redis...\n")

try:
    for message in consumer:
        event = message.value
        user = event.get('user_id')
        new_rating = event.get('rating')
        
        if user in mock_redis_state:
            old_total = mock_redis_state[user]["total_ratings"]
            old_avg = mock_redis_state[user]["avg_rating"]
            genre = mock_redis_state[user]["favorite_genre"] # Get the genre
            
            # 1. Real-time math
            new_total = old_total + 1
            new_avg = ((old_avg * old_total) + new_rating) / new_total
            
            mock_redis_state[user]["total_ratings"] = new_total
            mock_redis_state[user]["avg_rating"] = round(new_avg, 2)
            
            print(f"📥 User {user} rated {new_rating} stars. New Avg: {round(new_avg, 2)}")

            # 2. Package into Pandas DataFrame (NOW WITH GENRE!)
            event_df = pd.DataFrame([{
                "user_id": user,
                "total_ratings": new_total,
                "avg_rating": round(new_avg, 2),
                "favorite_genre": genre, # <--- Added to satisfy Feast!
                "event_timestamp": pd.Timestamp.utcnow() 
            }])

            # 3. Push directly into Redis!
            store.push("rating_push_source", event_df)
            print("   ✅ Successfully pushed to Redis Feature Store!\n")

except KeyboardInterrupt:
    print("\n🛑 Stopped listening.")
    consumer.close()