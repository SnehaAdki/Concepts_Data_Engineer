import pandas as pd

data = {'Country': ['Belgium',  'India',  'Brazil'],

'Capital': ['Brussels',  'New Delhi',  'Brasilia'],

'Population': [11190846, 1303171035, 207847528]} 

df = pd.DataFrame(data,columns=['Country',  'Capital',  'Population'],index=[1,2,3])
print(df)



print(df[0:])
print(df.iloc[[0]])
print(df.iloc[[0] , [2]])
print(df.iat[0,0])


print(df.loc[1,'Country'])
print(df.at[1,'Country'])

print(df.at[1, 'Country'])
print(df.iat[0, 1])
print(df.loc[0:2, ['Country', 'Capital']])
print(df.iloc[0:3,0:3])