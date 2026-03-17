import pandas as pd
import numpy as np
from datetime import datetime

# 1. Create dummy data
# We match the columns defined in definitions.py
data = {
    "user_id": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
    "total_ratings": [50, 12, 100, 4, 66, 55, 15, 105, 6, 70],
    "avg_rating": [4.5, 3.2, 2.5, 5.0, 3.8, 4.6, 3.3, 2.6, 4.9, 3.9],
    "favorite_genre": ["Action", "Comedy", "Horror", "Drama", "Sci-Fi", "Action", "Comedy", "Horror", "Drama", "Sci-Fi"],
    # Timestamps are crucial for Feast to know "when" this data was valid
    "event_timestamp": [
        datetime(2025, 1, 1), datetime(2025, 1, 1), datetime(2025, 1, 1), datetime(2025, 1, 1), datetime(2025, 1, 1),
        datetime(2025, 1, 2), datetime(2025, 1, 2), datetime(2025, 1, 2), datetime(2025, 1, 2), datetime(2025, 1, 2)
    ]
}

df = pd.DataFrame(data)

# 2. Save to the data folder
# This matches the path you put in definitions.py
df.to_parquet("data/user_stats.parquet")

print("✅ 'data/user_stats.parquet' created successfully!")
print(df.head())