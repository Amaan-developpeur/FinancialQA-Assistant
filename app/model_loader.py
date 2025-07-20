# app/model_loader.py

from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = np.load(BASE_DIR / "data" / "embedded_chunks.npy")
df_chunks = pd.read_csv(BASE_DIR / "data" / "extracted_chunks.csv")
