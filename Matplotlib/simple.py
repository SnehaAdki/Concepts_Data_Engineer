import matplotlib.pyplot as plt

x = [1,2,3,4,5,6] 
y = [1,4,6,8,10,12]

fig,ax = plt.subplots()
ax.plot(x,y,marker = 'o',label = "Data Points")
ax.set_label("Simple Example")
ax.set_xlabel("X-Axis")
ax.set_ylabel("Y-Axis")

plt.show()
