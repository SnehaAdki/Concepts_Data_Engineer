import matplotlib.pyplot as plt

cars = ['AUDI','BMW','FORD','TESLA','JAGUAR']
data = [23,10,30,10,10]

plt.pie(data , labels=cars)
plt.title("Cars Data")

plt.show()