import time
print("Hello from Docker!")
#time.sleep(100)  # Keeps container running for 60 seconds

with open("/data/output.txt", "w") as f:
    f.write("Hello, persistent Docker volume please re-confirm ??? !")
