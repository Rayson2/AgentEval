from pathlib import Path
from langchain.tools import tool

# Project root: agent-framework-research/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DOCUMENT_DIR = PROJECT_ROOT / "agenteval" / "backend" / "datasets" / "documents"


print("\n========== DOCUMENT DEBUG ==========")

print("__file__:", Path(__file__).resolve())
print("PROJECT_ROOT:", PROJECT_ROOT)
print("DOCUMENT_DIR:", DOCUMENT_DIR)
print("DIRECTORY EXISTS:", DOCUMENT_DIR.exists())

if DOCUMENT_DIR.exists():
    files = list(DOCUMENT_DIR.rglob("*"))

    print("TOTAL FILES:", len(files))

    for file in files:
        if file.is_file():
            print("FOUND:", file)

print("====================================\n")


@tool
def search_documents(query: str) -> str:
    """Search local research documents using relevant keywords."""

    if not DOCUMENT_DIR.exists():
        return "No research document directory found."

    keywords = set(query.lower().split())
    results = []

    for path in DOCUMENT_DIR.rglob("*"):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        score = sum(
            content.lower().count(word)
            for word in keywords
            if len(word) > 2
        )

        if score > 0:
            relative_path = path.relative_to(DOCUMENT_DIR)

            results.append({
                "id": relative_path.as_posix(),
                "score": score,
                "preview": content[:1200],
            })

    results.sort(key=lambda item: item["score"], reverse=True)

    if not results:
        return "No relevant documents found."

    output = []

    for item in results[:5]:
        output.append(
            f"DOCUMENT ID: {item['id']}\n"
            f"RELEVANCE SCORE: {item['score']}\n"
            f"CONTENT:\n{item['preview']}"
        )

    return "\n\n---\n\n".join(output)


@tool
def read_document(document_id: str) -> str:
    """Read the full contents of a research document by its ID."""

    try:
        base = DOCUMENT_DIR.resolve()
        path = (base / document_id).resolve()

        if not path.is_relative_to(base):
            return "Invalid document ID."

        if not path.is_file():
            return "Document not found."

        if path.suffix.lower() not in {".txt", ".md"}:
            return "Unsupported document format."

        return path.read_text(encoding="utf-8")

    except (OSError, UnicodeError, ValueError):
        return "Unable to read document."
