# ingestion/models.py
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime
import uuid

@dataclass
class Document:
    id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        text: str,
        metadata: Dict[str, Any]
    ) -> "Document":
        return Document(
            id=str(uuid.uuid4()),
            text=text,
            metadata=metadata
        )
