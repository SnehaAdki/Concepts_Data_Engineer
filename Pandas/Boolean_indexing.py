import pandas as pd


s = pd.Series([3, -5, 7, 6],  index=['a',  'b',  'c',  'd'])

s['a'] = 13
print(s)
print(s[~(s>=1)])

print(s [ (s < -1) | (s)])

# s=s.drop(['a'])
s.drop(['a'],inplace= True)
print("After Dropped")
print(s)


data = {'Country': ['Belgium',  'India',  'Brazil'],

'Capital': ['Brussels',  'New Delhi',  'Brasilia'],

'Population': [11190846, 1303171035, 207847528]} 

df = pd.DataFrame(data,columns=['Country',  'Capital',  'Population'],index=[1,2,3])

# df['1'] = 11190846
df.loc[1,'Population'] = 10000
print(df)
print(df [ df['Population'] <= 11190846 ] )

# print("Drop colplete columns")
# df.drop('Country',axis=1,inplace=True)
# print(df)
# df.drop(1,inplace=True)
# print(df)

print(df.rank())
print(df.index)
print(df.sum())
print(df.cumsum())
print(df.cummin())
print(df.cummax())

print(df.min())
print(df.max())

print(df.idxmax())
print(df.idxmin())

print("MEans")
print(df['Population'].mean())
print(df['Population'].median())
print(df.describe())