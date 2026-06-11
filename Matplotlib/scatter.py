import matplotlib.pyplot as plt

x = ['Thur','Frdi','Sat','Sun','Thur','Sat']
y = [100,80,120,130,70,110]

plt.scatter(x,y)
plt.title("Scattered Plot")
plt.xlabel("Days")
plt.ylabel("Total Bill")
plt.show()