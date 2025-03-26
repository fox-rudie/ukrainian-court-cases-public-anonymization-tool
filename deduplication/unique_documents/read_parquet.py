import pandas as pd
import os

python_file_path = os.path.dirname(os.path.abspath(__file__))

df = pd.read_parquet(f'{python_file_path}/2024-court-decisions.parquet')

print(df.head())

#print the number of rows
print(f'Number of rows: {df.shape[0]}')

# print first 10 texts
for index, row in df.head(3).iterrows():
    print(row['text'])
    print('-'*100)
