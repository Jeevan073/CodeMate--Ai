
import hashlib
import json
import logging
from pathlib import Path

from app.rag.document_loader import (
    DATA_DIR,
    SUPPORTED_EXTENSIONS,
    extract_text,
    detect_language,
)
from app.rag.preprocess import clean_text
from app.rag.chunking import create_splitter
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

BATCH_SIZE = 64

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = PROJECT_ROOT / "app" / "rag" / "ingestion_manifest.json"


class RAGPipeline:

    def __init__(
        self,
        data_dir=DATA_DIR,
        vector_store=None,
        manifest_path=None,
        embedding_generator=None
    ):
        self.data_dir = Path(data_dir)

        self.vector_store = (
            vector_store if vector_store is not None
            else VectorStore()
        )

        self.manifest_path = Path(manifest_path or DEFAULT_MANIFEST)

        self.embedding_generator = (
            embedding_generator
            if embedding_generator is not None
            else EmbeddingGenerator()
        )

        self.splitter = create_splitter()
        self.manifest = self._load_manifest()

    # MANIFEST MANAGEMENT

    def _load_manifest(self):
        if not self.manifest_path.exists():
            return {}

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                return data

            logger.warning("Invalid manifest format. Starting fresh.")
            return {}

        except (json.JSONDecodeError, OSError) as error:
            logger.warning("Could not read manifest: %s", error)
            return {}

    def _save_manifest(self):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.manifest_path, "w", encoding="utf-8") as file:
            json.dump(self.manifest, file, indent=2)
            file.flush()

    # FILE HASHING

    def _file_hash(self, file_path):
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as file:
            for block in iter(lambda: file.read(1024 * 1024), b""):
                sha256.update(block)

        return sha256.hexdigest()

    def _make_chunk_id(self, source, index):
        return hashlib.sha256(
            f"{source}_{index}".encode("utf-8")
        ).hexdigest()

    # DOCUMENT PROCESSING

    def process_file(self, file_path):
        text = extract_text(file_path)
        text = clean_text(text)

        if not text:
            return []

        metadata = {
            "source": str(file_path.relative_to(self.data_dir)),
            "filename": file_path.name,
            "language": detect_language(file_path),
            "file_type": file_path.suffix.lower().replace(".", "")
        }

        chunks = []
        text_chunks = self.splitter.split_text(text)

        for index, chunk_text in enumerate(text_chunks):
            if not chunk_text.strip():
                continue

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": index
                }
            })

        return chunks

    # VECTOR STORAGE

    def _store_batch(self, chunks):
        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_generator.generate_embeddings(texts)

        ids = [
            self._make_chunk_id(
                chunk["metadata"]["source"],
                chunk["metadata"]["chunk_index"]
            )
            for chunk in chunks
        ]

        self.vector_store.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks]
        )

    def _delete_file_chunks(self, source):
        self.vector_store.delete_by_source(source)

    # INCREMENTAL INGESTION

    def ingest(self):
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Documentation directory not found: {self.data_dir}"
            )

        total_new = 0
        total_updated = 0
        total_skipped = 0
        total_chunks = 0
        total_failed = 0

        current_files = set()

        for file_path in self.data_dir.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            source = str(file_path.relative_to(self.data_dir))
            current_files.add(source)

            try:
                file_hash = self._file_hash(file_path)
                previous_hash = self.manifest.get(source)

                if previous_hash == file_hash:
                    total_skipped += 1
                    continue

                chunks = self.process_file(file_path)

                if not chunks:
                    logger.warning("No text extracted: %s", source)
                    total_failed += 1
                    continue

                self._delete_file_chunks(source)

                for start in range(0, len(chunks), BATCH_SIZE):
                    batch = chunks[start:start + BATCH_SIZE]
                    self._store_batch(batch)
                    total_chunks += len(batch)

                self.manifest[source] = file_hash
                self._save_manifest()

                if previous_hash is None:
                    total_new += 1
                else:
                    total_updated += 1

                logger.info("Successfully ingested: %s", source)

            except Exception:
                total_failed += 1
                logger.exception("Failed to ingest: %s", source)

        deleted_files = set(self.manifest.keys()) - current_files

        for source in deleted_files:
            try:
                self._delete_file_chunks(source)
                del self.manifest[source]
                self._save_manifest()
                logger.info("Deleted outdated document: %s", source)

            except Exception:
                logger.exception("Failed to delete document: %s", source)

        return {
            "new_files": total_new,
            "updated_files": total_updated,
            "skipped_files": total_skipped,
            "failed_files": total_failed,
            "chunks_added": total_chunks,
            "database_count": self.vector_store.count()
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    pipeline = RAGPipeline()

    print("\n========== CODEMATE RAG PIPELINE ==========")
    print("Documentation directory:", pipeline.data_dir)
    print("Database collection:", pipeline.vector_store.collection.name)
    print("Existing database chunks:", pipeline.vector_store.count())
    print("Manifest entries:", len(pipeline.manifest))
    print("\nPipeline initialized successfully.")
    print("Full ingestion has NOT been started.")
