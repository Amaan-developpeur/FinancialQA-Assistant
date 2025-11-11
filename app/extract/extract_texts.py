# app/extract/extract_texts.py
import os
import csv
import time
import traceback
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

import pdfplumber
import pandas as pd
from tqdm import tqdm

# Config / paths (adjust if needed)
BASE_DIR = Path(__file__).resolve().parents[2]  # project root
RAW_DIR = BASE_DIR / "data" / "raw_docs"
OUTPUT_CSV = BASE_DIR / "data" / "extracted_chunks.csv"
ERROR_CSV = BASE_DIR / "data" / "error_log.csv"

# Chunking params
CHUNK_SIZE = 300     # words per chunk (tuneable)
OVERLAP = 50         # words overlap between chunks
MIN_WORDS = 30       # skip tiny fragments

# How many parallel processes to use. Set to None to auto-detect.
WORKERS = max(1, min(6, (os.cpu_count() or 2) - 1))

def chunk_text_words(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[Tuple[int, str]]:
    """
    Slide over words and produce (offset, chunk_text).
    Return list of (offset_index, chunk_text).
    """
    words = text.strip().split()
    chunks = []
    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size
    for start in range(0, max(0, len(words)), step):
        chunk_words = words[start:start + chunk_size]
        if len(chunk_words) < MIN_WORDS:
            continue
        chunk_text = " ".join(chunk_words)
        chunks.append((start, chunk_text))
        if start + chunk_size >= len(words):
            break
    return chunks

def extract_chunks_from_pdf(filepath: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract chunks from one PDF file.
    Returns (chunks_list, error_list).
    """
    chunks = []
    errors = []
    filename = os.path.basename(filepath)
    try:
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    text = page.extract_text()
                    if not text:
                        # record empty pages optionally
                        continue
                    # normalize whitespace
                    text = " ".join(text.split())
                    page_chunks = chunk_text_words(text, chunk_size=chunk_size, overlap=overlap)
                    for offset, chunk_text in page_chunks:
                        chunk_id = f"{filename}_p{page_num}_o{offset}"
                        chunks.append({
                            "filename": filename,
                            "page": page_num,
                            "chunk_id": chunk_id,
                            "text": chunk_text
                        })
                except Exception as e:
                    errors.append({
                        "filename": filename,
                        "page": page_num,
                        "error": f"page_error: {str(e)}"
                    })
    except Exception as e:
        errors.append({
            "filename": filename,
            "page": -1,
            "error": f"file_open_error: {str(e)}"
        })
    return chunks, errors

def _worker_wrapper(args):
    """Helper to call from ProcessPool (pickleable)"""
    filepath, chunk_size, overlap = args
    return extract_chunks_from_pdf(filepath, chunk_size, overlap)

def write_chunks_incremental(output_csv: Path, chunks: List[Dict], mode: str = "a"):
    """
    Append chunks list to CSV. Write header if file not exists.
    """
    if not chunks:
        return
    df = pd.DataFrame(chunks)
    header = not output_csv.exists()
    df.to_csv(output_csv, mode=mode, index=False, header=header, encoding="utf-8")

def write_errors_incremental(error_csv: Path, errors: List[Dict], mode: str = "a"):
    if not errors:
        return
    df = pd.DataFrame(errors)
    header = not error_csv.exists()
    df.to_csv(error_csv, mode=mode, index=False, header=header, encoding="utf-8")

def run_parallel_extraction(raw_dir: Path = RAW_DIR,
                            output_csv: Path = OUTPUT_CSV,
                            error_csv: Path = ERROR_CSV,
                            workers: int = WORKERS,
                            chunk_size: int = CHUNK_SIZE,
                            overlap: int = OVERLAP):
    raw_dir = Path(raw_dir)
    pdf_files = sorted([str(p) for p in raw_dir.glob("*.pdf")])
    if not pdf_files:
        print("No PDF files found in:", raw_dir)
        return

    # If present, remove previous output to start fresh
    if output_csv.exists():
        print(f"Appending to existing file: {output_csv}")
    else:
        print(f"Will create output file: {output_csv}")

    total_start = time.time()
    all_error_count = 0
    total_chunks = 0

    # Prepare args for workers
    args_list = [(fp, chunk_size, overlap) for fp in pdf_files]

    with ProcessPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(_worker_wrapper, args): args[0] for args in args_list}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Processing PDFs"):
            filepath = futures[fut]
            try:
                chunks, errors = fut.result()
                write_chunks_incremental(output_csv, chunks)
                write_errors_incremental(error_csv, errors)
                total_chunks += len(chunks)
                all_error_count += len(errors)
            except Exception as e:
                # this should be rare; log to error CSV
                tb = traceback.format_exc()
                write_errors_incremental(error_csv, [{"filename": os.path.basename(filepath), "page": -1, "error": f"worker_failed: {str(e)}\n{tb}"}])
                all_error_count += 1

    elapsed = time.time() - total_start
    print(f"Done. Extracted ~{total_chunks} chunks from {len(pdf_files)} files in {elapsed:.1f}s (workers={workers}).")
    if all_error_count:
        print(f"Encountered {all_error_count} errors; see {error_csv}")



if __name__ == "__main__":
    run_parallel_extraction()
