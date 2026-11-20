
from sentence_transformers import SentenceTransformer
class EmbeddingGenerator:

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str):
        """
        Generate embedding for one text.
        """
        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()

    def generate_embeddings(self, texts: list):
        """
        Generate embeddings in batches.
        """
        return self.model.encode(
            texts,
            batch_size=64,
            normalize_embeddings=True,
            show_progress_bar=True
        ).tolist()


if __name__ == "__main__":

    generator = EmbeddingGenerator()

    sample_texts = [
        "Python functions are reusable blocks of code.",
        "C++ supports object-oriented programming.",
        "Java provides exception handling."
    ]

    embeddings = generator.generate_embeddings(sample_texts)

    print("\n========== EMBEDDING REPORT ==========")
    print("Total embeddings:", len(embeddings))
    print("Embedding dimensions:", len(embeddings[0]))
    print("First embedding preview:", embeddings[0][:5])