import numpy as np
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging


BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_FILE = BASE_DIR / "data" / "embedded_chunks.npy"
CHUNKS_FILE = BASE_DIR / "data" / "extracted_chunks.csv"

#Logging Setup
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / "query_chunks.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger()

#Model Setup
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


try:
    embeddings = np.load(EMBEDDINGS_FILE)
    df_chunks = pd.read_csv(CHUNKS_FILE)
    logger.info(f"Loaded embeddings: {embeddings.shape}")
    logger.info(f"Loaded chunk metadata: {df_chunks.shape}")
except Exception as e:
    logger.exception(f"Failed to load embeddings or chunks: {str(e)}")
    raise



def get_top_k_similar_chunks(query, k=5):
    try:
        query_embedding = model.encode([query])
        similarity_scores = cosine_similarity(query_embedding, embeddings)[0]
        top_indices = similarity_scores.argsort()[::-1][:k]

        top_chunks = []
        for idx in top_indices:
            chunk = df_chunks.iloc[idx].to_dict()
            chunk["similarity"] = float(similarity_scores[idx])
            top_chunks.append(chunk)

        logger.info(f"Query: '{query}'")
        logger.info(f"Top {k} chunks retrieved")
        return pd.DataFrame(top_chunks)

    except Exception as err:
        logger.exception(f"Similarity search failed: {str(err)}")
        raise


