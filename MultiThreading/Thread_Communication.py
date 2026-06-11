import threading
import queue

q = queue.Queue()

def producer():
    for i in range(11):
        q.put(i)
        print(f"Produced..{i}")

def consumer():
    while True:
        item = q.get()
        print(f"consumed {item}")
        if item == 10:
            break


t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)

t1.start()
t2.start()

t1.join()
t2.join()

print("Exittt!....")
