import pandas as pd
import sys

# Check if the correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage: python script.py <input_csv> <output_parquet>")
    sys.exit(1)

# Get input CSV and output Parquet file paths
input_csv = sys.argv[1]
output_parquet = sys.argv[2]

# Read CSV file
df = pd.read_csv(input_csv)

# Write to Parquet file
df.to_parquet(output_parquet)

print(f"CSV file '{input_csv}' has been converted to Parquet file '{output_parquet}'.")
