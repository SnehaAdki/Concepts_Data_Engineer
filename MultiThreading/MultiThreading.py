import threading

def square( num ):
    print(num*num)


t1 = threading.Thread(target=square,args=(10,))
t2 = threading.Thread(target=square,args=(120,))
t4 = threading.Thread(target=square,args=(40,))
t3 = threading.Thread(target=square,args=(30,))

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

print("Done !.... ")
