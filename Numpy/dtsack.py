import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
res = np.dstack((a, b))
print("dstck with +ve number")
print(res)

a = np.array([[1,2],[7,8]])
b = np.array([[10,20],[70,80]])
res = np.dstack((a, b))
print("dstck with 2D array")
print(res)

a = np.array([-1, -2, -3])
b = np.array([4, 5, 6])
res = np.dstack((a, b))
print("dstck with -ve number")
print(res)
