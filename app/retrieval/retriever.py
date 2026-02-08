# retrieval/retriever.py
from typing import List, Dict, Any, Optional
import pickle
import numpy as np
import faiss

from app.ingestion.models import Document


class VectorStore:
    def __init__(self, index_path: str):
        self.index = faiss.read_index(f"{index_path}/index.faiss")
        with open(f"{index_path}/docs.pkl", "rb") as f:
            self.documents: List[Document] = pickle.load(f)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ):
        scores, indices = self.index.search(query_embedding, top_k)
        return scores[0], indices[0]


class Retriever:
    def __init__(self, vector_store: VectorStore, embedding_model):
        """
        embedding_model must expose:
        embed(texts: List[str]) -> np.ndarray
        """
        self.store = vector_store
        self.embedding_model = embedding_model

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        query_embedding = self.embedding_model.embed([query])

        scores, indices = self.store.search(query_embedding, top_k * 2)

        chunks = []
        chunk_scores = []
        metadatas = []

        for score, idx in zip(scores, indices):
            if idx == -1:
                continue

            doc = self.store.documents[idx]

            if metadata_filter and not self._metadata_match(
                doc.metadata, metadata_filter
            ):
                continue

            chunks.append(doc.text)
            chunk_scores.append(float(score))
            metadatas.append(doc.metadata)

            if len(chunks) >= top_k:
                break

        return {
            "chunks": chunks,
            "scores": chunk_scores,
            "metadata": metadatas
        }

    @staticmethod
    def _metadata_match(
        doc_metadata: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> bool:
        """
        Simple exact-match metadata filtering.
        Can be extended later to ranges / fuzzy logic.
        """
        for key, value in filters.items():
            if doc_metadata.get(key) != value:
                return False
        return True
