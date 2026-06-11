import numpy as np

a = np.array([-1, -2, -3])
b = np.array([4, 5])

res = np.hstack((a, b))
print("hstack with -ve")
print(res)

a = np.array([1,4])
b = np.array([4, 5])

res = np.hstack((a, b))
print("hstack with +ve")
print(res)

arr = np.array([[1,2],[3,4]])
arr1 = np.array([[5,6],[7,8]])

res = np.hstack((arr,arr1))
print("Result in the 2D array")
print(res)