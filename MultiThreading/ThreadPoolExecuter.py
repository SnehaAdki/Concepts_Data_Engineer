from concurrent.futures import ThreadPoolExecutor

def worker(task):
    print(f"Task {task} running")


with ThreadPoolExecutor(max_workers=3) as executor:
    executor.submit(worker,1)
    executor.submit(worker,2)
    executor.submit(worker,3)
