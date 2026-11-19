
from app.rag.vector_store import VectorStore

store = VectorStore()

# Read existing records
records = store.collection.get(
    include=["documents", "metadatas"]
)

sample_ids = []

for record_id, document, metadata in zip(
    records["ids"],
    records["documents"],
    records["metadatas"]
):
    filename = metadata.get("filename", "")

    if filename in ["python_sample.txt", "cpp_sample.txt"]:
        sample_ids.append(record_id)

    elif document in [
        "Python functions are reusable blocks of code.",
        "C++ supports object-oriented programming."
    ]:
        sample_ids.append(record_id)

# Delete only identified sample records
if sample_ids:
    store.collection.delete(ids=sample_ids)

print("Sample records deleted:", len(sample_ids))
print("Remaining production chunks:", store.count())
