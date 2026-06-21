class A:
    def execute(self):
        print("A's Execution....")

class B:
    def execute(self):
        print("B's Execution....")

class C:
    def execute(self,ide):
        ide.execute()


a = A()
b = B()

c = C()
c.execute(a)
c.execute(b)