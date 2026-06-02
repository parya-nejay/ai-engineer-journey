"""
loader.py - Load multiple documents from a folder.

Currently supports: .txt files
Next step: add .pdf support
"""
from pathlib import Path
from pypdf import PdfReader


def load_documents(docs_folder: str = "docs") -> list[dict]:
    """
    Load all supported documents from a folder.

    Args:
        docs_folder: path to the folder containing documents

    Returns:
        A list of dicts, one per document:
        [
            {"text": "...", "source": "handbook.txt"},
            {"text": "...", "source": "product_faq.txt"},
        ]
    """
    folder = Path(docs_folder)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {docs_folder}")

    documents = []

    # Walk through every file in the folder
    for file_path in folder.iterdir():
        # Skip subfolders and hidden files
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

       # Handle .txt files
        if suffix == ".txt":
            text = file_path.read_text(encoding="utf-8")
            documents.append({
                "text": text,
                "source": file_path.name,
            })

        # Handle .pdf files
        elif suffix == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # some pages can be empty (e.g., images only)
                    text += page_text + "\n"
            documents.append({
                "text": text,
                "source": file_path.name,
            })

        else:
            # Skip files we don't know how to read yet
            print(f"⚠️  Skipping unsupported file: {file_path.name}")

    return documents


# Test block — runs only when you execute this file directly
if __name__ == "__main__":
    docs = load_documents("docs")
    print(f"\n✅ Loaded {len(docs)} document(s):\n")
    for doc in docs:
        char_count = len(doc["text"])
        preview = doc["text"][:80].replace("\n", " ")
        print(f"  📄 {doc['source']} ({char_count} chars)")
        print(f"     Preview: {preview}...\n")