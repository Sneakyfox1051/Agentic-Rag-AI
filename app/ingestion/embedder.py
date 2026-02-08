# ingestion/embedder.py
from typing import List
import os
import pickle

import numpy as np
import faiss

from app.ingestion.models import Document


class EmbeddingModel:
    """
    Replace this with OpenAI / HF / local model later.
    """
    def embed(self, texts: List[str]) -> np.ndarray:
        # Dummy embedding (replace!)
        return np.random.rand(len(texts), 768).astype("float32")


class VectorStore:
    def __init__(self, dim: int, index_path: str = "vector_index"):
        self.dim = dim
        self.index_path = index_path
        self.index = faiss.IndexFlatL2(dim)
        self.documents: List[Document] = []

    def add(self, embeddings: np.ndarray, docs: List[Document]):
        self.index.add(embeddings)
        self.documents.extend(docs)

    def save(self):
        os.makedirs(self.index_path, exist_ok=True)
        faiss.write_index(self.index, f"{self.index_path}/index.faiss")

        with open(f"{self.index_path}/docs.pkl", "wb") as f:
            pickle.dump(self.documents, f)


def index_documents(
    docs: List[Document],
    index_path: str = "vector_index"
) -> VectorStore:
    """
    Main callable function as requested.
    """
    model = EmbeddingModel()
    texts = [d.text for d in docs]

    embeddings = model.embed(texts)

    store = VectorStore(
        dim=embeddings.shape[1],
        index_path=index_path
    )

    store.add(embeddings, docs)
    store.save()

    return store
