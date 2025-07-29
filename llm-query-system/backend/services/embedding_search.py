from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_texts(texts: list[str]) -> np.ndarray:
    return model.encode(texts)

def search_similar(query: str, documents: list[str], top_k: int = 5) -> list[tuple[str, float]]:
    doc_embeddings = embed_texts(documents)
    query_embedding = embed_texts([query])[0].reshape(1, -1)

    scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = scores.argsort()[::-1][:top_k]

    return [(documents[i], float(scores[i])) for i in top_indices]
