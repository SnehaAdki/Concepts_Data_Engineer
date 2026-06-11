# consumer_confluent.py
from threading import Event,Thread

from confluent_kafka import Producer,Consumer

stop_event = Event()
from_sneha = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
})

to_vijay_topic = Producer({'bootstrap.servers': 'localhost:9092'})


def consume_from_sneha():
    from_sneha.subscribe(['sneha_topic'])
    while not stop_event.is_set():
        msg = from_sneha.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
        else:
            print(f"{msg.value().decode()[8:]}")


def produce_to_vijay_topic():
    print("Vijay -> Sneha:")
    while not stop_event.is_set():
        try:
            input_val = input()
        except EOFError:
            stop_event.set()
            break

        if not input_val.strip():
            continue

        to_vijay_topic.produce('vijay_topic', f'Message {input_val}'.encode())
        to_vijay_topic.flush()

try:
    consumer_thread = Thread(target=consume_from_sneha, daemon=True)
    consumer_thread.start()

    produce_to_vijay_topic()
except KeyboardInterrupt:
    pass
finally:
    stop_event.set()
    from_sneha.close()
    to_vijay_topic.flush()