import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import logging


BASE_DIR = Path(__file__).resolve().parents[1]
CHUNKS_CSV = BASE_DIR / "data" / "extracted_chunks.csv"
EMBEDDINGS_OUTPUT = BASE_DIR / "data" / "embedded_chunks.npy"
METADATA_OUTPUT = BASE_DIR / "data" / "embedded_chunks.csv"



MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 32


LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / "embed_chunks.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger()



def load_chunk_data(path):
    if not path.exists():
        logger.error(f"Chunk file not found at {path}")
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)

def encode_chunks(model, texts, batch_size):
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
    return np.vstack(embeddings)

# Execution Block

if __name__ == "__main__":
    try:
        logger.info("Loading extracted chunks...")
        df_embed = load_chunk_data(CHUNKS_CSV)

        if "text" not in df_embed.columns:
            logger.error("'text' column missing from input CSV")
            raise ValueError("Missing required column: text")

        texts = df_embed["text"].tolist()

        logger.info(f"Loading model: {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)

        logger.info(f"Encoding {len(texts)} chunks...")
        embedding_matrix = encode_chunks(model, texts, BATCH_SIZE)
        np.save(EMBEDDINGS_OUTPUT, embedding_matrix)

        df_embed["embedding_index"] = range(len(df_embed))
        df_embed.to_csv(METADATA_OUTPUT, index=False)

        logger.info(f"Saved {embedding_matrix.shape[0]} embeddings to {EMBEDDINGS_OUTPUT}")
        logger.info(f"Metadata saved to {METADATA_OUTPUT}")

    except Exception as e:
        logger.exception(f"Embedding script failed: {str(e)}")
