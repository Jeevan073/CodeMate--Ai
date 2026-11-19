
import tempfile
import shutil
import gc

import chromadb

from app.rag.embeddings import EmbeddingGenerator


def run_test():
    print("\nStarting incremental ingestion test...")

    # Create temporary database directory
    temp_dir = tempfile.mkdtemp()
    client = None

    try:
        client = chromadb.PersistentClient(path=temp_dir)

        collection = client.get_or_create_collection(
            name="incremental_test",
            metadata={"hnsw:space": "cosine"}
        )

        generator = EmbeddingGenerator()

        def store_file(source, text):
            embedding = generator.generate_embedding(text)

            collection.upsert(
                ids=[f"{source}_0"],
                documents=[text],
                embeddings=[embedding],
                metadatas=[{"source": source}]
            )

        # TEST 1: First insertion
        print("\nTEST 1: First insertion")

        store_file(
            "sample.py",
            "Python functions are reusable."
        )

        print("Database count:", collection.count())

        # TEST 2: Duplicate insertion
        print("\nTEST 2: Duplicate insertion")

        store_file(
            "sample.py",
            "Python functions are reusable."
        )

        print("Database count:", collection.count())

        # TEST 3: Update document
        print("\nTEST 3: Document update")

        store_file(
            "sample.py",
            "Python classes support object-oriented programming."
        )

        print("Database count:", collection.count())

        result = collection.get(
            where={"source": "sample.py"},
            include=["documents"]
        )

        print("Updated content:", result["documents"])

        # TEST 4: Delete document
        print("\nTEST 4: Document deletion")

        collection.delete(
            where={"source": "sample.py"}
        )

        print("Database count:", collection.count())

        print("\nAll storage tests completed successfully!")

    finally:
        # Release ChromaDB handles before deleting files
        client = None
        gc.collect()

        try:
            shutil.rmtree(temp_dir)
            print("Temporary database cleaned successfully.")
        except PermissionError:
            print("Temporary database cleanup deferred.")
            print("You can manually delete:", temp_dir)


if __name__ == "__main__":
    run_test()
