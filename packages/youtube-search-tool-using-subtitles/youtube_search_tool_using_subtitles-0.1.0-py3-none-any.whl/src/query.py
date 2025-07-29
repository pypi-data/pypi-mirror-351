import os
import sys
import json
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from langchain_chroma import Chroma

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
USE_EMBEDDING_PROVIDER: str = os.getenv("USE_EMBEDDING_PROVIDER", "openai").strip().lower()
LOCAL_EMBEDDING_MODEL: str = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
CHROMA_DB_DIRECTORY = PROJECT_ROOT / "chroma_db"
MODELS_CACHE_DIR = PROJECT_ROOT / "models"
CACHE_DIR = PROJECT_ROOT / "cache"

if ENABLE_CACHING:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_embedding_fn():
    """Return the embedding function specified in the .env file."""
    if USE_EMBEDDING_PROVIDER == "local":
        return HuggingFaceEmbeddings(
            model_name=LOCAL_EMBEDDING_MODEL,
            cache_folder=str(MODELS_CACHE_DIR / "embeddings"),
            encode_kwargs={"normalize_embeddings": True},
        )

    # Default – OpenAI
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set but is required for OpenAI embeddings.")
    return OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")

def _cache_path(query: str) -> Path:
    return CACHE_DIR / f"{hash(query) % 10000}.json"


def get_cached_result(query: str) -> Optional[dict]:
    if not ENABLE_CACHING:
        return None
    path = _cache_path(query)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except Exception:
            pass
    return None


def cache_result(query: str, result: str) -> None:
    if not ENABLE_CACHING:
        return
    try:
        with open(_cache_path(query), "w", encoding="utf-8") as fp:
            json.dump({"query": query, "result": result}, fp, ensure_ascii=False, indent=2)
    except Exception as exc:
        print(f"[warn] Failed to cache result – {exc}")

def format_response(search_results: List) -> str:
    if not search_results:
        return "No results found."

    lines: List[str] = []
    for i, doc in enumerate(search_results, 1):
        lines.extend(
            [
                f"**Result #{i}**",
                f"💬 \"{doc.page_content}\"",
                f"⏰ {doc.metadata.get('timestamp', 'Unknown')}",
                f"🔗 {doc.metadata.get('link', 'No link')}",
                "---",
            ]
        )
    return "\n".join(lines)

def main() -> None:
    if not CHROMA_DB_DIRECTORY.exists():
        print(f"❌  Chroma DB directory '{CHROMA_DB_DIRECTORY}' not found – have you created the database?")
        return

    # Grab the query -----------------------------------------------------------
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your query: ").strip()

    if not user_query:
        print("Please enter a valid query.")
        return

    # Check cache --------------------------------------------------------------
    if (cached := get_cached_result(user_query)) is not None:
        print("📋  (cached)")
        print(cached["result"])
        return

    # Perform search -----------------------------------------------------------
    try:
        embedding_fn = get_embedding_fn()
        db = Chroma(persist_directory=str(CHROMA_DB_DIRECTORY), embedding_function=embedding_fn)
        results = db.similarity_search(user_query, k=10)  # bump k so you see more mentions

        if not results:
            print(f"No results found for '{user_query}'.")
            return

        response = format_response(results)
        cache_result(user_query, response)
        print(response)

    except Exception as exc:
        print(f"Error querying the database: {exc}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
