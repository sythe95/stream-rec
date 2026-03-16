import json
import time
import random
from kafka import KafkaProducer

# Connect to the Redpanda container exposed on port 9092
producer = KafkaProducer(
    bootstrap_servers=['redpanda:29092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic_name = 'user_ratings'

print("🎬 Starting StreamRec Live Rating Generator...")
print(f"Streaming data to topic: '{topic_name}' (Press Ctrl+C to stop)\n")

try:
    while True:
        # Generate a fake rating event
        event = {
            "user_id": random.randint(1, 5),  # Sticking to Users 1-5 for our test data
            "movie_id": random.randint(100, 999),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "timestamp": int(time.time())
        }
        
        # Fire it into the message broker
        producer.send(topic_name, event)
        print(f"📤 Sent: {event}")
        
        # Pause for 2 seconds to simulate a steady stream of traffic
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Stopped generating ratings.")
    producer.close()