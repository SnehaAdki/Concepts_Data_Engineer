
class A:
    def __init__(self):
        print("A's init")
    
    def ss(self):
        print("apart init")

class B(A):
    def __init__(self):
        super().ss()
        print("B's init")


b = B()
a = A()