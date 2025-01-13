
# Project Title: Document Collection and Processing Pipeline

This project automates downloading `.rtf` files from URLs in a CSV file, converts them directly to `.txt` format, and compresses every 1,000 processed files into an archive. It is designed to be resilient to interruptions, resuming from the last processed file.

## Prerequisites

Ensure that you have **Docker** installed on your machine. This setup uses Docker to create an isolated environment for running the script.

## 1. Setting Up the Project Directory

Make sure the project directory has the following structure:

```
project_directory/
│
├── Dockerfile                   # Dockerfile to set up the environment
├── environment.yml              # Conda environment configuration file
├── collection.py                # Python script with the processing code
└── data/
    ├── documents.csv            # CSV file with URLs for downloading documents
    └── output/                  # Directory for processed `.txt` files (auto-created by Docker)
```

## 2. Docker Setup

### Dockerfile

The Dockerfile installs Miniconda and sets up a Conda environment for `collection.py`. It uses `conda run` to ensure the Conda environment is activated when running the script. Be sure to replace `"your_environment_name"` in the Dockerfile with the actual environment name specified in `environment.yml`.

## 3. Building and Running the Docker Container

1. **Build the Docker Image**:

   Run the following command in your project directory to build the Docker image:

   ```bash
   docker build -t document_processor .
   ```

2. **Run the Container with Command-Line Arguments**:

   After building, you can run the container and pass command-line arguments directly. For example:

   ```bash
   docker run --rm -v /path/to/your/data:/app/data document_processor --csv_path /app/data/documents.csv --output_dir /app/data/output --batch_size 1000
   ```

   Replace `/path/to/your/data` with the path to your local data directory. This command mounts your local directory, allowing access to `documents.csv` and saving output files back to your machine.

## Command-line Arguments

- `--csv_path`: Path to the CSV file containing the URLs. Docker specifies this as `/app/data/documents.csv`.
- `--output_dir`: Directory where the raw and processed documents will be stored. Docker specifies this as `/app/data/output`.
- `--batch_size`: Number of files to process before compressing into an archive. Defaults to `1000`. 

## Script Functionality
   - Each `.rtf` file is immediately converted to `.txt` format without saving the original `.rtf`.
   - Every `batch_size` number of `.txt` files are compressed into a `.zip` archive and removed from the folder to manage storage.

## Resuming after Interruption
   - The script automatically saves progress in a checkpoint file (`progress_checkpoint.txt`). If the process is interrupted, rerun the container, and it will continue from the last completed file.

---

## Additional Information

- **Compression**: Each batch of `batch_size` `.txt` files is archived into `documents_batch_<batch_number>.zip` in the specified `output_dir` directory.
- **Error Handling**: If any file download or conversion fails, the script will record progress up to the last successfully processed file.

This setup ensures a reliable and manageable processing pipeline with easy resumption in case of interruptions.
