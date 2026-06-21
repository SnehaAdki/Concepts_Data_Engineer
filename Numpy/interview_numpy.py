from numpy import *


print("With array()")
arr = array([10,20,30,40],'i')
print(arr)


print("With linspace()")
arr1 = linspace(1,20,10)
print(arr1)

print("With logspace()")
arr1 = logspace(1,20,10)
print(arr1)

print("With arange()")
arr1 = arange(1,20,10)
print(arr1)

mat_arr = matrix(arr)
print(mat_arr)

mat_arr2 = matrix(arr)
print(mat_arr2)

mat_sum = mat_arr + mat_arr2
print(mat_sum)

mat_sub = mat_arr - mat_arr2
print(mat_sub)

two_d = matrix([[1,2,3], [7,8,9]])
print(two_d)

two_d1 = matrix([[10,20,30], [70,80,90], [7,8,9]])
print(two_d1)

# print(two_d +two_d1) # for addition r & c should be equal to another r & c
print(two_d *two_d1) # c1 should be equal to r2 