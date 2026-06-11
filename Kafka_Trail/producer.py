from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send messages
for i in range(10):
    message = {'number': i, 'message': f'Hello Kafka {i}'}
    producer.send('my-python-topic', value=message)
    print(f"Sent: {message}")

producer.flush()
producer.close()
print("All messages sent!")