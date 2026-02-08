# ingestion/chunker.py
from typing import List
from copy import deepcopy

from app.ingestion.models import Document


def simple_tokenizer(text: str) -> List[str]:
    """
    Placeholder tokenizer.
    Replace with tiktoken or HF tokenizer later.
    """
    return text.split()


def detokenize(tokens: List[str]) -> str:
    return " ".join(tokens)


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 300,
    overlap: int = 50
) -> List[Document]:
    """
    Split documents into token-based chunks.
    Each chunk preserves parent metadata.
    """
    chunks: List[Document] = []

    for doc in documents:
        tokens = simple_tokenizer(doc.text)
        start = 0

        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]

            chunk_text = detokenize(chunk_tokens)

            chunk_metadata = deepcopy(doc.metadata)
            chunk_metadata.update({
                "parent_doc_id": doc.id,
                "chunk_start": start,
                "chunk_end": end
            })

            chunks.append(
                Document.create(
                    text=chunk_text,
                    metadata=chunk_metadata
                )
            )

            start += chunk_size - overlap

    return chunks
