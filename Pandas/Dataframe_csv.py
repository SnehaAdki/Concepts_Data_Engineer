import pandas as pd

data = {'Country': ['Belgium',  'India',  'Brazil'],

'Capital': ['Brussels',  'New Delhi',  'Brasilia'],

'Population': [11190846, 1303171035, 207847528]} 

df = pd.DataFrame(data,columns=['Country',  'Capital',  'Population'],index=[1,2,3])
print(df)

# write to csv file
df.to_csv("County.csv")

# read the same csv file 

data = pd.read_csv('/Users/SAI15/Desktop/Concepts/County.csv',index_col=0)
print("Read from the CSV")
print(data)