import seaborn as sns
import matplotlib.pyplot as plt 

tips = sns.load_dataset('tips')
sns.histplot(tips['total_bill'],kde=True)
plt.show()