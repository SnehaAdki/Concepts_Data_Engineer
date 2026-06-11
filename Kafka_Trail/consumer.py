from kafka import KafkaConsumer
import json


def safe_deserialize(message_bytes):
    text = message_bytes.decode('utf-8')
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text

consumer = KafkaConsumer(
    'my-python-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',  # Read from beginning
    group_id='my-python-group',
    value_deserializer=safe_deserialize
)

print("Listening for messages... (Ctrl+C to exit)")
try:
    print(consumer.topics())
    for message in consumer:
        print(f"Received: {message.value}")
        # print(f"Received: {message.value} | Partition: {message.partition} | Offset: {message.offset}")
except KeyboardInterrupt:
    print("Stopped.")
finally:
    consumer.close()