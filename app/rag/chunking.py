
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_splitter():
    """
    Create a reusable text splitter.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            " ",
            ""
        ],
        length_function=len
    )


def split_document(document, splitter=None):
    """
    Split one document into chunks.

    Preserves source and language metadata.
    """

    if splitter is None:
        splitter = create_splitter()

    text = document["text"]
    metadata = document["metadata"]

    text_chunks = splitter.split_text(text)

    for index, chunk in enumerate(text_chunks):

        if not chunk.strip():
            continue

        yield {
            "text": chunk,
            "metadata": {
                **metadata,
                "chunk_index": index
            }
        }
if __name__ == "__main__":

    sample = {
        "text": """
        Python Functions

        A function is a reusable block of code.

        def greet(name):
            print("Hello", name)

        Functions can accept parameters and return values.
        """ * 100,

        "metadata": {
            "filename": "sample.txt",
            "language": "python",
            "file_type": "txt"
        }
    }

    chunks = list(split_document(sample))

    print("\n========== CHUNKING REPORT ==========")
    print("Total chunks:", len(chunks))

    for chunk in chunks[:2]:
        print("\nMetadata:", chunk["metadata"])
        print("Content:", chunk["text"][:200])
