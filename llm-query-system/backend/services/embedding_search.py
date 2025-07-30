from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_texts(texts: list[str]) -> np.ndarray:
    return model.encode(texts)

def search_similar_chunks(query: str, documents: list[str], top_k: int = 5) -> list[tuple[str, float]]:
    doc_embeddings = embed_texts(documents)
    query_embedding = embed_texts([query])[0].reshape(1, -1)

    scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = scores.argsort()[::-1][:top_k]

    return [(documents[i], float(scores[i])) for i in top_indices]

import json

def embed_and_store_chunks(chunks: list[str], output_path: str) -> None:
    embeddings = embed_texts(chunks)
    data = [
        {"chunk": chunk, "embedding": emb.tolist()}
        for chunk, emb in zip(chunks, embeddings)
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


