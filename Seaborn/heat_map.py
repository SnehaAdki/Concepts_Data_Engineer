import seaborn as sns
import matplotlib.pyplot as mp

data = sns.load_dataset('tips')
corr = data.corr(numeric_only=True)

sns.heatmap(corr, annot=True,cmap="coolwarm")
mp.show()