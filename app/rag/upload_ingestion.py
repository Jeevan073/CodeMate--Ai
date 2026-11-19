
from pathlib import Path

from app.rag.preprocess import clean_text
from app.rag.chunking import create_splitter
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore


LANGUAGE_MAP = {
    ".py": "python",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".java": "java",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "typescript",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".txt": "text"
}


class UploadedCodeIndexer:

    def __init__(self, vector_store=None, embedding_generator=None):
        self.vector_store = vector_store or VectorStore()
        self.embedding_generator = (
            embedding_generator or EmbeddingGenerator()
        )
        self.splitter = create_splitter()

    def ingest_uploaded_file(
        self,
        file_id: str,
        file_path: str,
        original_filename: str
    ):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Uploaded file not found: {path}"
            )

        extension = path.suffix.lower()
        language = LANGUAGE_MAP.get(extension)

        if not language:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        text = path.read_text(encoding="utf-8-sig")
        text = clean_text(text)

        if not text:
            raise ValueError("Uploaded file contains no readable text.")

        text_chunks = self.splitter.split_text(text)

        if not text_chunks:
            raise ValueError("No chunks generated from uploaded file.")

        source = f"upload:{file_id}"

        chunks = []

        for index, chunk_text in enumerate(text_chunks):
            if not chunk_text.strip():
                continue

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": source,
                    "source_type": "uploaded_file",
                    "file_id": file_id,
                    "filename": original_filename,
                    "file_type": extension.lstrip("."),
                    "language": language,
                    "chunk_index": index
                }
            })

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_generator.generate_embeddings(
            texts
        )

        ids = [
            f"upload_{file_id}_{chunk['metadata']['chunk_index']}"
            for chunk in chunks
        ]

        # Store only uploaded-file chunks.
        # Existing documentation IDs and chunks are not modified.
        self.vector_store.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                chunk["metadata"] for chunk in chunks
            ]
        )

        return {
            "success": True,
            "file_id": file_id,
            "filename": original_filename,
            "language": language,
            "chunks_created": len(chunks)
        }


# Shared indexer
uploaded_code_indexer = UploadedCodeIndexer()
    