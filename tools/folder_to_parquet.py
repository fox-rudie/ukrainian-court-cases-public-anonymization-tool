import os
import pandas as pd
import re
import argparse

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

def folder_to_parquet(input_folder, output_path):
    # read files and create list of dictionaries
    documents = []
    filenames = os.listdir(input_folder)
    
    for filename in filenames:
        file_path = os.path.join(input_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                documents.append({
                    'id': filename.split('.')[0],
                    'text': normalize_file(f.read())
                })
            except:
                print(f'Error reading {filename}')

    df = pd.DataFrame(documents)
    df = df.sort_values('id').reset_index(drop=True)  # Sort by id and reset index
    df.to_parquet(output_path)

def main():
    parser = argparse.ArgumentParser(
        description='Convert a folder of text files to a single parquet file. Each file becomes a row with filename as id.'
    )
    parser.add_argument('input_folder', help='Path to the folder containing text files')
    parser.add_argument('output_path', help='Path where the parquet file should be saved')
    
    args = parser.parse_args()
    folder_to_parquet(args.input_folder, args.output_path)

if __name__ == '__main__':
    main()
