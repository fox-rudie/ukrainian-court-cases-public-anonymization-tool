import os
import re
import argparse
import logging
from datasketch import MinHash, MinHashLSH
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def normalize_text(text):
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize_text(text):
    return re.findall(r'\b\w+\b', text.lower())

def process_file(file_path, num_perm):
    """Reads file, tokenizes, and returns its MinHash signature."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        minhash = MinHash(num_perm=num_perm)
        for word in tokenize_text(normalize_text(file_content)):
            minhash.update(word.encode('utf-8'))
        return file_path, minhash
    except Exception as e:
        logging.warning(f"Error processing file {file_path}: {e}")
        return None


def append_unique_to_file(unique_store, file_path):
    if not os.path.exists(unique_store):
        with open(unique_store, 'w', encoding='utf-8') as f:
            f.write(f"{file_path}\n")
    else:
        with open(unique_store, 'a', encoding='utf-8') as f:
            f.write(f"{file_path}\n")


def process_futures(futures, lsh, unique_store, unique_files, duplicates, original_to_duplicates, processed_count):
    for future in as_completed(futures):
        result = future.result()
        if result:
            file_path, minhash = result
            query_result = lsh.query(minhash)
            if query_result:
                canonical = query_result[0]
                # original_to_duplicates.setdefault(canonical, []).append(file_path)
                # duplicates.append(file_path)
            else:
                lsh.insert(file_path, minhash)
                unique_files.append(file_path)
                append_unique_to_file(unique_store, file_path)
            processed_count += 1
            if processed_count % 1000 == 0:
                logging.info(f"Processed {processed_count} files")
    return processed_count


def deduplicate_text_files_lsh(folder_path, threshold=0.5, num_perm=128, workers=4,
                               limit=None, use_threads=False, batch_size=1000, unique_store="unique_files.txt"):
    """
    Deduplicates text files using MinHashLSH with parallelism.
    Processes files in batches so progress logging happens continuously.
    """
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    duplicates = []
    unique_files = []
    original_to_duplicates = {}

    file_paths = [entry.path for entry in os.scandir(folder_path) if entry.is_file()]
    if limit:
        file_paths = file_paths[:limit]

    total_files = len(file_paths)
    logging.info(f"Processing {total_files} files with {workers} workers...")
    Executor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    processed_count = 0
    with Executor(max_workers=workers) as executor:
        futures = []
        for file_path in file_paths:
            futures.append(executor.submit(process_file, file_path, num_perm))
            if len(futures) >= batch_size:
                processed_count = process_futures(futures, lsh, unique_store, unique_files, duplicates, original_to_duplicates, processed_count)
                futures = []
        # Process any remaining futures.
        if futures:
            processed_count = process_futures(futures, lsh, unique_store, unique_files, duplicates, original_to_duplicates, processed_count)

    return duplicates, unique_files, original_to_duplicates, total_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate text files using MinHash LSH")
    parser.add_argument("folder", type=str, help="Folder containing text files")
    parser.add_argument("--threshold", type=float, default=0.5, help="Similarity threshold (0-1)")
    parser.add_argument("--num_perm", type=int, default=128, help="Number of MinHash permutations")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to process (for testing)")
    parser.add_argument("--use_threads", action="store_true", help="Use threads instead of processes")
    parser.add_argument("--batch_size", type=int, default=1000, help="Batch size for processing futures")
    parser.add_argument("--output", type=str, default="unique_files.txt", help="Output file to write unique file names")

    args = parser.parse_args()

    duplicates, unique_files, original_to_duplicates, total_files = deduplicate_text_files_lsh(
        args.folder, args.threshold, args.num_perm, args.workers,
        args.limit, args.use_threads, args.batch_size, args.output
    )

    dup_percentage = (len(unique_files) / total_files * 100) if total_files > 0 else 0
    logging.info(f"Threshold: {args.threshold}")
    logging.info(f"Duplicates: {len(duplicates)}")
    logging.info(f"Unique files: {len(unique_files)}")
    logging.info(f"Unique files percentage: {dup_percentage:.2f}%")


    # for i in range(10):
    #     print(original_to_duplicates[list(original_to_duplicates.keys())[i]])
    # # Write unique file names to the output file.
    # try:
    #     with open(args.output, 'w', encoding='utf-8') as f:
    #         for file_name in unique_files:
    #             f.write(f"{file_name}\n")
    #     logging.info(f"Unique file names written to {args.output}")
    # except Exception as e:
    #     logging.error(f"Error writing to output file {args.output}: {e}")
