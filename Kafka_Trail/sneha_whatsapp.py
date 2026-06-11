from threading import Event, Thread
from confluent_kafka import Consumer, Producer


stop_event = Event()

from_vijay = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
})

to_sneha_topic = Producer({'bootstrap.servers': 'localhost:9092'})


def consume_from_vijay():
    from_vijay.subscribe(['vijay_topic'])
    print(stop_event)
    while not stop_event.is_set():
        msg = from_vijay.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
        else:
            print(f"{msg.value().decode()[8:]}")


def produce_to_sneha_topic():
    print("Sneha -> vijay")
    while not stop_event.is_set():
        try:
            input_val = input()
        except EOFError:
            stop_event.set()
            break

        if not input_val.strip():
            continue

        to_sneha_topic.produce('sneha_topic', f'Message {input_val}'.encode())
        to_sneha_topic.flush()


try:
    consumer_thread = Thread(target=consume_from_vijay, daemon=True)
    consumer_thread.start()
    produce_to_sneha_topic()
except KeyboardInterrupt:
    pass
finally:
    stop_event.set()
    from_vijay.close()
    to_sneha_topic.flush()