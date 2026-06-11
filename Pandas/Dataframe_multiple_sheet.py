import pandas as pd

data = {'Country': ['Belgium',  'India',  'Brazil'],

'Capital': ['Brussels',  'New Delhi',  'Brasilia'],

'Population': [11190846, 1303171035, 207847528]} 

df = pd.DataFrame(data,index=['p1','p2','p3'])
print(df)

with pd.ExcelWriter(
    '/Users/SAI15/Desktop/Concepts/Country_det.xlsx',
    mode='a',
    engine='openpyxl',
    if_sheet_exists='replace'
) as writer:
    df.to_excel(writer,sheet_name='Duplicated_sheet_4',index= False)

sheets =  pd.ExcelFile('/Users/SAI15/Desktop/Concepts/Country_det.xlsx')

for i in sheets.sheet_names:
    df = pd.read_excel('/Users/SAI15/Desktop/Concepts/Country_det.xlsx',i)
    print(i)
    print(df)