
import re
import unicodedata


def clean_text(text: str) -> str:
    """Clean documentation text without damaging code formatting."""

    if not isinstance(text, str):
        return ""

    # Normalize Unicode characters
    text = unicodedata.normalize("NFC", text)

    # Remove null bytes and BOM
    text = text.replace("\x00", "")
    text = text.replace("\ufeff", "")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Fix a known encoding issue
    text = text.replace("Â¶", "¶")

    # Remove trailing spaces while preserving indentation
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def preprocess_documents(documents):
    """Clean documents while preserving their metadata."""

    processed_documents = []

    for document in documents:
        original_text = document.get("text", "")
        cleaned_text = clean_text(original_text)

        if not cleaned_text:
            continue

        processed_documents.append({
            "text": cleaned_text,
            "metadata": {
                **document.get("metadata", {}),
                "original_char_count": len(original_text),
                "cleaned_char_count": len(cleaned_text)
            }
        })

    return processed_documents


if __name__ == "__main__":
    sample_documents = [
        {
            "text": "def greet():   \r\n    print('Hello')\r\n\r\n\r\n",
            "metadata": {
                "filename": "sample.py",
                "language": "python"
            }
        }
    ]

    result = preprocess_documents(sample_documents)

    print("\n========== PREPROCESSING REPORT ==========")
    print("Documents processed:", len(result))
    print("Cleaned text:")
    print(result[0]["text"])
    print("Metadata:", result[0]["metadata"])
