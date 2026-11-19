
import logging
from pathlib import Path

import fitz
from bs4 import BeautifulSoup
from docx import Document

logger = logging.getLogger(__name__)

# Project root: CodeMate-AI
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Documentation directory
DATA_DIR = PROJECT_ROOT / "app" / "rag" / "data"

SUPPORTED_EXTENSIONS = {
    ".html",
    ".htm",
    ".pdf",
    ".txt",
    ".md",
    ".rst",
    ".docx",
}

LANGUAGES = {
    "python",
    "java",
    "c",
    "cpp",
    "sql",
}


def detect_language(file_path: Path) -> str:
    """
    Detect programming language from the parent folder.
    """
    for part in file_path.parts:
        folder = part.lower()

        if folder in LANGUAGES:
            return folder

        if folder in {"c++", "cplusplus"}:
            return "cpp"

    return "unknown"


def extract_text(file_path: Path) -> str:
    """
    Extract text according to the document format.
    """

    extension = file_path.suffix.lower()

    if extension in {".html", ".htm"}:
        html = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        soup = BeautifulSoup(html, "html.parser")

        # Remove unnecessary elements
        for element in soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            element.decompose()

        return soup.get_text(
            separator="\n",
            strip=True
        )

    elif extension == ".pdf":
        text_parts = []

        with fitz.open(file_path) as pdf:
            for page in pdf:
                text_parts.append(page.get_text())

        return "\n".join(text_parts)

    elif extension in {".txt", ".md", ".rst"}:
        return file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    elif extension == ".docx":
        document = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
        ]

        return "\n".join(paragraphs)

    return ""


def load_documents(data_dir: Path = DATA_DIR) -> list:
    """
    Load all supported documents recursively.

    Returns:
        List of dictionaries containing text and metadata.
    """

    documents = []

    if not data_dir.exists():
        logger.error("Documentation directory not found: %s", data_dir)
        return documents

    for file_path in data_dir.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            text = extract_text(file_path)

            if not text or not text.strip():
                logger.warning("Empty document: %s", file_path)
                continue

            metadata = {
                "source": str(file_path.relative_to(data_dir)),
                "filename": file_path.name,
                "language": detect_language(file_path),
                "file_type": file_path.suffix.lower().replace(".", "")
            }

            documents.append({
                "text": text,
                "metadata": metadata
            })

            logger.info("Loaded: %s", file_path.name)

        except Exception as error:
            logger.exception(
                "Failed to load %s: %s",
                file_path,
                error
            )

    logger.info("Total documents loaded: %d", len(documents))

    return documents



if __name__ == "__main__":
    from collections import Counter

    logging.basicConfig(level=logging.WARNING)

    docs = load_documents()

    print("\n========== INGESTION REPORT ==========")

    language_counts = Counter(
        doc["metadata"]["language"] for doc in docs
    )

    language_characters = Counter()

    for doc in docs:
        language = doc["metadata"]["language"]
        language_characters[language] += len(doc["text"])

    for language in ["c", "cpp", "java", "python", "sql"]:
        print(f"\nLanguage: {language.upper()}")
        print("Documents:", language_counts[language])
        print("Extracted characters:",
              language_characters[language])

    print("\nTotal documents:", len(docs))
    print("Total characters:", sum(
        len(doc["text"]) for doc in docs
    ))
