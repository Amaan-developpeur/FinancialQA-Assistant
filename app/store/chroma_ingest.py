# app/store/chroma_ingest.py
import pandas as pd
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from tqdm import tqdm
from chromadb import PersistentClient
import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"



# ========== PATHS ==========
BASE_DIR = Path(__file__).resolve().parents[2]
CHUNKS_CSV = BASE_DIR / "data" / "extracted_chunks.csv"
VECTOR_DIR = BASE_DIR / "data" / "vector_store"

# ========== CHROMA CONFIG ==========
client = PersistentClient(path=str(VECTOR_DIR))

COLLECTION_NAME = "financial_chunks"

# Recreate or get collection
try:
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Loaded existing Chroma collection: {COLLECTION_NAME}")
except:
    collection = client.create_collection(COLLECTION_NAME)
    print(f"Created new Chroma collection: {COLLECTION_NAME}")

# ========== EMBEDDING MODEL ==========
model = SentenceTransformer("all-MiniLM-L6-v2")

# ========== INGEST FUNCTION ==========
def ingest_chunks_to_chroma(chunks_csv=CHUNKS_CSV, batch_size=128):
    df = pd.read_csv(chunks_csv)
    print(f"Loaded {len(df)} chunks from {chunks_csv.name}")

    ids = df["chunk_id"].tolist()
    texts = df["text"].tolist()
    metadatas = df[["filename", "page"]].to_dict(orient="records")

    # If collection already has some data, skip existing IDs
    existing_ids = set(collection.get(ids=None)["ids"])
    new_data = [(i, t, m) for i, t, m in zip(ids, texts, metadatas) if i not in existing_ids]
    print(f"Inserting {len(new_data)} new chunks into ChromaDB...")

    for i in tqdm(range(0, len(new_data), batch_size), desc="Embedding + Inserting"):
        batch = new_data[i:i+batch_size]
        batch_ids, batch_texts, batch_meta = zip(*batch)
        embeddings = model.encode(batch_texts, batch_size=32, show_progress_bar=False)
        collection.add(
            ids=list(batch_ids),
            documents=list(batch_texts),
            metadatas=list(batch_meta),
            embeddings=np.vstack(embeddings)
        )
    print(f"Done. Chroma persisted at: {VECTOR_DIR}")

if __name__ == "__main__":
    ingest_chunks_to_chroma()
