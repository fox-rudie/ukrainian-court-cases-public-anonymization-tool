import argparse
import csv
import logging
import os
import requests
from tqdm import tqdm
from striprtf.striprtf import rtf_to_text
import tarfile
import sys

# Set up logging configuration
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,  # Adjust level as needed (DEBUG, INFO, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)
# Set up argument parsing
parser = argparse.ArgumentParser(description="Download, convert, and process RTF files from a CSV file.")
parser.add_argument("--csv_path", type=str, required=True, help="Path to the CSV file containing URLs.")
parser.add_argument("--output_dir", type=str, default="2024", help="Output directory for storing processed files.")
parser.add_argument("--batch_size", type=int, default=1000, help="Number of files to process before compressing.")
args = parser.parse_args()

# Paths and configurations from arguments
csv_path = args.csv_path
output_dir = args.output_dir
batch_size = args.batch_size
processed_documents_dir = os.path.join(output_dir, "documents")
checkpoint_file = os.path.join(output_dir, "progress_checkpoint.txt")
url_column = 9  # Assuming URL column is the 10th in the CSV file

# Ensure output directories exist
os.makedirs(processed_documents_dir, exist_ok=True)

# Load progress checkpoint
def load_checkpoint():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return int(f.read().strip())
    return 0

# Save progress checkpoint
def save_checkpoint(index):
    with open(checkpoint_file, 'w') as f:
        f.write(str(index))

# Batch compression function
def compress_batch(batch_number):
    tar_filename = os.path.join(output_dir, f'documents_batch_{batch_number}.tar.gz')
    with tarfile.open(tar_filename, 'w:gz') as tar:
        for file in os.listdir(processed_documents_dir):
            if file.endswith('.txt'):
                full_path = os.path.join(processed_documents_dir, file)
                tar.add(full_path, arcname=file)
                os.remove(full_path)

# Start processing
start_index = load_checkpoint()
batch_number = start_index // batch_size

# Count total lines in the CSV for progress tracking
with open(csv_path, 'r') as csvfile:
    total_lines = sum(1 for _ in csvfile)
logging.info(f"Total number of lines in CSV: {total_lines}")

with open(csv_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i < start_index:
            continue  # Skip already processed files

        data = row[0].split("\t")
        name = data[0]
        download_url = data[url_column]

        if download_url.endswith('.rtf'):
            response = requests.get(download_url)
            rtf_content = response.content.decode('cp1251', errors='ignore')
            text = rtf_to_text(rtf_content)

            # Save directly as text
            with open(os.path.join(processed_documents_dir, f'{name}.txt'), 'w') as outfile:
                outfile.write(text)
        
        # Save progress checkpoint
        save_checkpoint(i + 1)
        
        # Log progress at each step
        logging.info(f"Processed file {i + 1}/{total_lines} - {name}")

        # Compress every batch_size files
        if (i + 1) % batch_size == 0:
            compress_batch(batch_number)
            batch_number += 1
            logging.info(f"Compressed batch {batch_number}")

# Final compression of remaining files
if os.listdir(processed_documents_dir):
    compress_batch(batch_number)
    logging.info(f"Final batch compression complete.")
