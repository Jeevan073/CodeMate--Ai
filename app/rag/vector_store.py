
import chromadb
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = PROJECT_ROOT / "chroma_db"


class VectorStore:

    def __init__(
        self,
        collection_name="codemate_docs",
        persist_directory=None
    ):
        if persist_directory is None:
            persist_directory = CHROMA_DIR

        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks, embeddings):
        """Add or update document chunks."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings count must match"
            )

        if not chunks:
            return

        ids = [
            f"{chunk['metadata'].get('source', chunk['metadata'].get('filename', 'doc'))}"
            f"_{chunk['metadata'].get('chunk_index', i)}"
            for i, chunk in enumerate(chunks)
        ]

        self.collection.upsert(
            ids=ids,
            documents=[chunk["text"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                chunk["metadata"] for chunk in chunks
            ]
        )

    def search(self, query_embedding, n_results=5, language=None):
        """Search for similar document chunks."""

        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": min(
                n_results,
                self.collection.count()
            )
        }

        if self.collection.count() == 0:
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        if language:
            query_args["where"] = {
                "language": language.lower()
            }

        return self.collection.query(**query_args)

    def delete_by_source(self, source):
        """Delete all chunks belonging to a document."""

        self.collection.delete(
            where={"source": source}
        )

    def count(self):
        """Return the total number of stored chunks."""

        return self.collection.count()


if __name__ == "__main__":

    store = VectorStore()

    print("\n========== VECTOR STORE REPORT ==========")
    print("Collection:", store.collection.name)
    print("Stored chunks:", store.count())
    print("Database location:", CHROMA_DIR)
