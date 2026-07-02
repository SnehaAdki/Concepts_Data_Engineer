import sys

class Student:
    pass

s1 = Student()
s1.name = 'Sneha'
s1.age = 20

print(s1)
print(s1.__dict__)
print(id(s1.name))
print(id(s1.age))
print(sys.getsizeof(s1) + sys.getsizeof(s1.__dict__))

class SlotStudent:
    __slot__ = ('name' , 'age' , 'id')

s1 = SlotStudent()

s1.name = 'Vj'
s1.age = 25
s1.id = 1

print(s1)
print(id(s1.name))
print(id(s1.age))
print(id(s1.id))
print(sys.getsizeof(s1))

name = 'Xj'
age = 15
id_1 = 2
print(sys.getsizeof(name) + sys.getsizeof(age) + sys.getsizeof(id_1))
