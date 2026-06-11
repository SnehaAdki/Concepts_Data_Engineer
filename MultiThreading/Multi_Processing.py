import multiprocessing as mp
import pandas as pd
MAX_WORKER = 3
MAX_CHUNK = 100

def process_data(ds_queue,i):
    while True:
        items = ds_queue.get()
        if items is None:
            print(f"No data {i}")
            break
        print(len(items), i)

        

def consumer(ds_queue):
    workers = []
    for i in range(MAX_WORKER):
        worker = mp.Process(
            target=process_data,
            args=(ds_queue,i)
        )
        worker.start()
        workers.append(worker)
    return workers

def producer(ds_queue):
    for chunk in pd.read_csv('/Users/SAI15/Desktop/Concepts/MultiThreading/multiprocessing_sample.csv', chunksize=MAX_CHUNK):
        ds_queue.put(chunk.to_dict(orient="records"))  # Convert DataFrame to list of dicts
    # Send stop signals to workers
    for _ in range(MAX_WORKER):
        ds_queue.put(None)
    # print(ds_queue)

def create_worker():
    ds_queue = mp.Queue(maxsize=MAX_CHUNK)
    
    producer(ds_queue)
    workers = consumer(ds_queue)
    for worker in workers:
        worker.join()

if __name__ == "__main__":
    create_worker()
    print("File processing done")
