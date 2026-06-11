from kafka.admin import KafkaAdminClient, NewTopic

admin_client = KafkaAdminClient(
    bootstrap_servers='localhost:9092',
    client_id='my-admin'
)

# Create topic
sneha_topic = NewTopic(
    name='sneha_topic',
    num_partitions=3,
    replication_factor=1
)

vijay_topic = NewTopic(
    name='vijay_topic',
    num_partitions=3,
    replication_factor=1
)


try:
    admin_client.create_topics(new_topics=[vijay_topic], validate_only=False)
    admin_client.create_topics(new_topics=[sneha_topic], validate_only=False)
    print("Topic 'sneha_topic' and 'vijay_topic' created successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    admin_client.close()