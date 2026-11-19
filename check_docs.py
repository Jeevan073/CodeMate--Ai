
from pathlib import Path
from collections import Counter

DATA_DIR = Path("app/rag/data")

print("\n======= CODEMATE DOCUMENTATION REPORT =======")

total = 0

for language_dir in DATA_DIR.iterdir():

    if not language_dir.is_dir():
        continue

    files = [
        f for f in language_dir.rglob("*")
        if f.is_file()
    ]

    extensions = Counter(
        f.suffix.lower() or "[no extension]"
        for f in files
    )

    print(f"\n{language_dir.name.upper()}")
    print("Total files:", len(files))

    for ext, count in extensions.most_common():
        print(f"  {ext}: {count}")

    total += len(files)

print("\nTotal files across languages:", total)
