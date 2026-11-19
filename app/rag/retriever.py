
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore


class CodeRetriever:
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()

    def retrieve(self, query, language=None, top_k=5):
        query_embedding = self.embedding_generator.generate_embedding(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k,
            language=language
        )

        retrieved_chunks = []

        if not results["documents"] or not results["documents"][0]:
            return retrieved_chunks

        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            retrieved_chunks.append({
                "text": document,
                "metadata": metadata,
                "distance": distance
            })

        return retrieved_chunks


if __name__ == "__main__":
    retriever = CodeRetriever()

    results = retriever.retrieve(
        query="How do Python functions work?",
        language="python",
        top_k=3
    )

    print("\n========== RETRIEVAL REPORT ==========")
    print("Retrieved chunks:", len(results))

    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}")
        print("Language:", result["metadata"].get("language"))
        print("Content:", result["text"])
        print("Distance:", result["distance"])
