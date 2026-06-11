# importing Numpy package
import numpy as np

# Create a 2-D Numpy array using np.array()
org_array = np.array([[99, 22, 33],
                      [44, 77, 66]])

# Copying org_array to copy_array
# using Assignment operator
copy_array = org_array

# modifying org_array
org_array[1, 2] = 13

# checking if copy_array has remained the same

# printing original array
print('Original Array: \n', org_array)

# printing copied array
print('\nCopied Array: \n', copy_array)

copy_array[0] = 100
print("id's")
print(id(org_array))
print(id(copy_array))
print(org_array)
print(copy_array)