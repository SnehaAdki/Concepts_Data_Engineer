# importing Numpy package
import numpy as np

# Creating a numpy array using np.array()
org_array = np.array([1.54, 2.99, 3.42, 4.87, 6.94,
                      8.21, 7.65, 10.50, 77.5])

print("Original array: ")

# printing the Numpy array
print(org_array)

# Now copying the org_array to copy_array
# using np.copy() function
copy_array = np.copy(org_array)

print("\nCopied array: ")

# printing the copied Numpy array
print(copy_array)

copy_array[0] = 100
print("id's")
print(id(org_array))
print(id(copy_array))
print(org_array)
print(copy_array)
