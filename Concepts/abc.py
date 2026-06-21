from abc import ABC , abstractmethod


class cc(ABC):
    @abstractmethod
    def do(self):
        print(".....")

class actual(cc):
    def do(self):
        print("re-deinged...")

a = actual()
a.do()

#c = cc() Can't instantiate abstract class cc without an implementation for abstract method 'do'