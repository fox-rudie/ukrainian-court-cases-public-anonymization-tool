import os
import pandas as pd
import re
python_file_path = os.path.dirname(os.path.abspath(__file__))

filenames = os.listdir(f'{python_file_path}/supreme_all/')

def normalize_file(file): 
    # Remove non-utf-8 characters
    file = file.encode('utf-8', 'ignore').decode('utf-8')
    # Replace multiple (more than 1) \n with a single \n
    file = re.sub(r'\n\s*\n+', '\n\n', file)   # collapse multiple blank lines to double newline (paragraphs)
    file = re.sub(r'[ \t]+', ' ', file)        # replace only spaces/tabs
    file = re.sub(r' *\n *', '\n', file)       # trim spaces around newlines
    # Remove leading and trailing spaces
    file = file.strip()
    return file

# read files and create list of dictionaries
documents = []
for filename in filenames:
    with open(f'{python_file_path}/supreme_all/{filename}', 'r', encoding='utf-8') as f:
        try:
            documents.append({
                'id': filename.split('.')[0],
                'text': normalize_file(f.read())
            })
        except:
            print(f'Error reading {filename}')

df = pd.DataFrame(documents)
df = df.sort_values('id').reset_index(drop=True)  # Sort by id and reset index
df.to_parquet(f'{python_file_path}/2024-supreme-court-decisions.parquet') 
