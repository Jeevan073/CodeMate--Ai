
import tempfile
import shutil
import gc
from pathlib import Path

from app.rag.pipeline import RAGPipeline
from app.rag.vector_store import VectorStore
from app.rag.embeddings import EmbeddingGenerator


def run_test():

    print("\n========== INCREMENTAL PIPELINE TEST ==========")

    temp_dir = Path(tempfile.mkdtemp())
    client = None

    try:
        # Create isolated test directories
        data_dir = temp_dir / "documents"
        db_dir = temp_dir / "test_db"
        manifest_path = temp_dir / "test_manifest.json"

        data_dir.mkdir()

        # Create temporary vector store
        vector_store = VectorStore(
            collection_name="pipeline_test",
            persist_directory=db_dir
        )

        client = vector_store.client

        # Initialize pipeline with temporary resources
        pipeline = RAGPipeline(
            data_dir=data_dir,
            vector_store=vector_store,
            manifest_path=manifest_path,
            embedding_generator=EmbeddingGenerator()
        )

        # TEST 1: New document
        print("\nTEST 1: New document")

        sample_file = data_dir / "python.txt"

        sample_file.write_text(
            "Python functions are reusable blocks of code.",
            encoding="utf-8"
        )

        report = pipeline.ingest()

        print("New files:", report["new_files"])
        print("Database chunks:", report["database_count"])

        assert report["new_files"] == 1
        assert report["database_count"] >= 1

        # TEST 2: Unchanged document
        print("\nTEST 2: Unchanged document")

        report = pipeline.ingest()

        print("Skipped files:", report["skipped_files"])

        assert report["skipped_files"] == 1
        assert report["new_files"] == 0

        # TEST 3: Modified document
        print("\nTEST 3: Modified document")

        sample_file.write_text(
            "Python classes support object-oriented programming.",
            encoding="utf-8"
        )

        report = pipeline.ingest()

        print("Updated files:", report["updated_files"])
        print("Database chunks:", report["database_count"])

        assert report["updated_files"] == 1

        results = vector_store.collection.get(
            where={"source": "python.txt"},
            include=["documents"]
        )

        print("Updated content:", results["documents"])

        assert any(
            "object-oriented programming" in doc
            for doc in results["documents"]
        )

        # TEST 4: Fewer chunks after modification
        print("\nTEST 4: Remove stale chunks")

        long_text = (
            "Python documentation explains functions and classes. "
            * 150
        )

        sample_file.write_text(long_text, encoding="utf-8")
        pipeline.ingest()

        long_count = vector_store.collection.count()

        sample_file.write_text(
            "Python is a programming language.",
            encoding="utf-8"
        )

        pipeline.ingest()

        short_count = vector_store.collection.count()

        print("Chunks before shortening:", long_count)
        print("Chunks after shortening:", short_count)

        assert short_count < long_count

        # TEST 5: Deleted document
        print("\nTEST 5: Deleted document")

        sample_file.unlink()

        report = pipeline.ingest()

        print("Database chunks after deletion:",
              report["database_count"])

        assert report["database_count"] == 0

        print("\nALL INCREMENTAL PIPELINE TESTS PASSED!")

    finally:
        # Release database handles before cleanup
        client = None
        vector_store = None
        pipeline = None

        gc.collect()

        try:
            shutil.rmtree(temp_dir)
            print("Temporary test files cleaned successfully.")
        except PermissionError:
            print("Temporary folder cleanup deferred:")
            print(temp_dir)


if __name__ == "__main__":
    run_test()
