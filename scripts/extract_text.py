import os
import pdfplumber
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import logging
import traceback

# CONFIGURATION
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw_docs"
OUTPUT_FILE = BASE_DIR / "data" / "extracted_chunks.csv"
ERROR_LOG_FILE = BASE_DIR / "data" / "error_log.csv"

CHUNK_SIZE = 300
OVERLAP = 50
MIN_CHUNK_LENGTH = 30

# LOGGER SETUP
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "extract_text.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CHUNKING FUNCTION
def extract_chunks_from_page(text, filename, page_num, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.strip().split()
    chunks = []
    for x in range(0, len(words), chunk_size - overlap):
        chunk_words = words[x:x + chunk_size]
        if len(chunk_words) < MIN_CHUNK_LENGTH:
            continue
        chunk_text = " ".join(chunk_words)
        chunk_id = f"{filename}_p{page_num}_c{x}"
        chunks.append({
            "filename": filename,
            "page": page_num,
            "chunk_id": chunk_id,
            "text": chunk_text
        })
    return chunks

# EXTRACTION DRIVER
def extract_text_from_pdf(raw_dir):
    all_chunks = []
    error_log = []
    pdf_files = [f for f in os.listdir(raw_dir) if f.lower().endswith(".pdf")]

    for filename in tqdm(pdf_files, desc="Extracting PDFs"):
        file_path = os.path.join(raw_dir, filename)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text()
                        if not text:
                            continue
                        text = text.replace("\n", " ").strip()
                        chunks = extract_chunks_from_page(text, filename, page_num)
                        all_chunks.extend(chunks)
                    except Exception as page_err:
                        error_log.append({
                            "filename": filename,
                            "page": page_num,
                            "error": f"{page_err}\n{traceback.format_exc()}"
                        })
        except Exception as file_err:
            error_log.append({
                "filename": filename,
                "page": -1,
                "error": f"{file_err}\n{traceback.format_exc()}"
            })

    return all_chunks, error_log

# ENTRYPOINT
if __name__ == "__main__":
    logger.info("Starting PDF extraction pipeline...")
    
    if not RAW_DIR.exists():
        logger.error(f"Raw directory not found: {RAW_DIR}")
        exit(1)

    chunks, errors = extract_text_from_pdf(RAW_DIR)

    # Save extracted chunks
    df = pd.DataFrame(chunks)
    df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"Extracted {len(df)} chunks → {OUTPUT_FILE}")

    # Save error logs (if any)
    if errors:
        error_df = pd.DataFrame(errors)
        error_df.to_csv(ERROR_LOG_FILE, index=False)
        logger.warning(f"Logged {len(error_df)} extraction errors → {ERROR_LOG_FILE}")
    else:
        logger.info("No extraction errors encountered.")
