# ingestion/loader.py
from pathlib import Path
from datetime import datetime
from typing import List

import docx
import PyPDF2

from app.ingestion.models import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def load_documents(path: str) -> List[Document]:
    """
    Load PDFs and DOCX files from a file or directory.
    Returns a list of Document objects.
    """
    base_path = Path(path)
    files = []

    if base_path.is_dir():
        files = [f for f in base_path.rglob("*") if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    else:
        files = [base_path]

    documents: List[Document] = []

    for file_path in files:
        text = extract_text(file_path)
        if not text.strip():
            continue

        metadata = {
            "source_file": file_path.name,
            "source_path": str(file_path.resolve()),
            "file_type": file_path.suffix.lower().replace(".", ""),
            "ingested_at": datetime.utcnow().isoformat()
        }

        documents.append(
            Document.create(
                text=text,
                metadata=metadata
            )
        )

    return documents


def extract_text(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        return extract_pdf(file_path)
    elif file_path.suffix.lower() == ".docx":
        return extract_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")


def extract_pdf(file_path: Path) -> str:
    text = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def extract_docx(file_path: Path) -> str:
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
