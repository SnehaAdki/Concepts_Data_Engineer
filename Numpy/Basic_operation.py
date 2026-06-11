import numpy as np
import functools

a = np.array([[2,2],[3,4]])
b = np.array([[4,3],[2,1]])

print("Adding to a ")
print(a+1)


print("Adding both")
print(a+b)

print("Substracting to b")
print(b-1)

print("Sum of all elements")
print(a.sum())


print("Greater\n", a>b)
print("Greater Equal\n", a>=b)
print("Less\n", a<b)
print("Less Equal\n", a<=b)
print("Reduce",functools.reduce(np.union1d,a))
print("Unique",np.unique(a))
print("Unique 1d",np.union1d(a,b))