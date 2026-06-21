abc = [10,20,30,40]

a = iter(abc)

print(a.__next__())
print(a.__next__())
print(a.__next__())
print(a.__next__())


def gen(arr):
    n = 0
    while n < len(arr):
        yield arr[n]
        n +=1


v = gen(abc)
for i in v : 
    print(i)