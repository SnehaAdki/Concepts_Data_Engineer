import matplotlib.pyplot as plt

x = ['Wed','Thur','Fri','Sat','Sun'] 
y = [50,170,120,250,190]

plt.bar(x,y)
plt.title("Bar chart ")
plt.xlabel("Days")
plt.ylabel("Bills")

plt.show()
