from app.rag.retriever import CodeRetriever

retriever = CodeRetriever()

query = "How do I define a function in Python?"

results = retriever.retrieve(
    query=query,
    language="python",
    top_k=5
)

print("\n========== RAG RETRIEVAL TEST ==========")

for i, result in enumerate(results, 1):
    print(f"\nResult {i}")
    print("Source:", result["metadata"]["source"])
    print("Distance:", result["distance"])
    print("Content:", result["text"][:500])