
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
    def search(
        self,
        query_embedding,
        n_results=5,
        language=None,
        file_id=None
    ):
        """Search documentation or a specific uploaded file."""

        total_count = self.collection.count()

        if total_count == 0:
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        where_conditions = []

        # The documentation index stores C++ as "cpp", while the API and
        # LLM contract use the conventional display value "c++".
        normalized_language = language.lower().strip() if language else None
        if normalized_language == "c++":
            normalized_language = "cpp"

        # A file ID scopes retrieval to one upload. Do not additionally filter
        # by the selected language: uploaded formats such as JavaScript or
        # Markdown may not match the current LLM language selector.
        if normalized_language and not file_id:
            where_conditions.append({
                "language": normalized_language
            })

        if file_id:
            where_conditions.append({
                "file_id": file_id
            })

        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, total_count)
        }

        if len(where_conditions) == 1:
            query_args["where"] = where_conditions[0]

        elif len(where_conditions) > 1:
            query_args["where"] = {
                "$and": where_conditions
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
