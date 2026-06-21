from functools import reduce

x = 10

print("Applying lambda...")
value = (lambda x : x + 20)
print(value(x))

arr = [10,20,30,55,33,50]
print("Array is ...... ")
print(arr)

print("filter() using lambda ... ")
values = list(filter(lambda x :x%5==0,arr ))
print(values)

print("map() using lambda ... ")
values = list(map(lambda x :x-5,arr ))
print(values)


print("reduce() using lambda ... ")
values = reduce(lambda x,y: x+y , arr)
print(values)