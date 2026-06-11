import numpy as np 

arr1 = np.array([[16,3],[7,8]],dtype=np.int64)

arr2 = np.array([[8,7],[2,3]],dtype=np.float64)

print("Addint both")
add = np.add(arr1,arr2)
print(add)

print("Sum of all elements")
total = np.sum(arr1)
print(total)

print("Square Root of all elements")
sqrt = np.sqrt(arr1)
print(sqrt)

print("Transpoe")
transposed_arr = arr1.T
print(transposed_arr)

print("sub both array")
sub = arr1-arr2
print(sub)


