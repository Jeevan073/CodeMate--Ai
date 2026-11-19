
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore


class CodeRetriever:

    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()

    def retrieve(
        self,
        query,
        language=None,
        top_k=5,
        file_id=None
    ):
        query_embedding = self.embedding_generator.generate_embedding(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k,
            language=language,
            file_id=file_id
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
