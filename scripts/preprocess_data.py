# scripts/preprocess_data.py
import cudf
import pandas as pd
from confluent_kafka import Consumer, Producer

# Configure Kafka consumer
consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'data-processor',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['raw-data'])

# Process and clean training data
def preprocess_batch(df):
    # Convert to cuDF for GPU acceleration if possible
    try:
        gdf = cudf.DataFrame.from_pandas(df)
        # Clean and process data
        gdf = gdf.dropna()
        # Return to pandas for compatibility
        return gdf.to_pandas()
    except:
        # Fallback to pandas if cuDF fails (for AMD GPU)
        df = df.dropna()
        return df

# Save processed data for fine-tuning
processed_data = []
while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue
    
    # Process message and save to file
    data = json.loads(msg.value().decode('utf-8'))
    df = pd.DataFrame([data])
    processed = preprocess_batch(df)
    processed_data.append(processed)
    
    # Save batch when sufficient data collected
    if len(processed_data) >= 1000:
        combined = pd.concat(processed_data)
        combined.to_json('/data/processed/training_data.jsonl', orient='records', lines=True)
        processed_data = []