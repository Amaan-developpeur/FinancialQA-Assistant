# app/query_engine.py

from sklearn.metrics.pairwise import cosine_similarity
from app.model_loader import model, embeddings, df_chunks

def get_top_k_similar_chunks(question: str, k: int = 5):
    query_embedding = model.encode([question])
    similarity = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = similarity.argsort()[::-1][:k]

    top_chunks = []
    for idx in top_indices:
        chunk = df_chunks.iloc[idx].to_dict()
        chunk["similarity"] = float(similarity[idx])
        top_chunks.append(chunk)
    return top_chunks
