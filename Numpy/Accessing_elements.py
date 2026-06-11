import numpy as np

arr = np.array([[-1,2,0,4],
                [4,-0.5,6,0],
                [2.6,0,7,8],
                [3,-7,4,2.0]])

print(arr)

print("Alternate columns")
arr2 = arr[:2,::2]
print(arr2)

print("Incides of all like (1,3) , (1,2), (0,1), (3,0)")
arr3 = arr[[1,1,0,3],
           [3,2,1,0]]
print(arr3)