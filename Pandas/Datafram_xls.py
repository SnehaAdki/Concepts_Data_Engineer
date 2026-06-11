import pandas as pd

data = {'Country': ['Belgium',  'India',  'Brazil'],

'Capital': ['Brussels',  'New Delhi',  'Brasilia'],

'Population': [11190846, 1303171035, 207847528]} 

df = pd.DataFrame(data,columns=['Country',  'Capital',  'Population'],index=[1,2,3])
print(df)

df.to_excel("Country_det.xlsx")

print("Reading from excels")
data = pd.read_excel('/Users/SAI15/Desktop/Concepts/Country_det.xlsx',index_col=0)
print(data)