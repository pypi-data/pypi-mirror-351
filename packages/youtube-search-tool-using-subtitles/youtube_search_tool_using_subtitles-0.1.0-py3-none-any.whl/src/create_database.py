import os
import re
import pandas as pd
from pathlib import Path
import google.generativeai as genai
from langchain_chroma import Chroma

from langchain.schema import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent 

load_dotenv(ROOT_DIR / '.env')

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
USE_EMBEDDING_PROVIDER = os.getenv("USE_EMBEDDING_PROVIDER", "openai").strip().lower()
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
SUBTITLES_FOLDER = PROJECT_ROOT / "subtitles"
CHROMA_DB_DIRECTORY = PROJECT_ROOT / "chroma_db"
MODELS_CACHE_DIR = PROJECT_ROOT / "models"
METADATA_FILE = "subtitles_metadata.csv"

# Create directories
SUBTITLES_FOLDER.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIRECTORY.mkdir(parents=True, exist_ok=True)
MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def parse_srt_file(file_path: Path):
    """
    Simple, fast SRT parsing
    """
    video_id = file_path.stem
    subtitles = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

    blocks = content.strip().split("\n\n")
    
    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            try:
                timestamp_line = lines[1]
                start_time_match = re.search(r"\((\d+)\)", timestamp_line)
                
                if start_time_match:
                    start_time = int(start_time_match.group(1))
                else:
                    continue
                
                visible_timestamp = timestamp_line.split(" (")[0]
                text = " ".join(lines[2:])
                link = f"https://youtu.be/{video_id}?t={start_time}"

                subtitles.append({
                    "video_id": video_id,
                    "start_time": start_time,
                    "timestamp": visible_timestamp,
                    "text": text,
                    "link": link
                })            
                
            except Exception as e:
                print(f"Error parsing block: {e}")
                continue
    
    return subtitles

def get_embedding_function():
    """
    Returns the appropriate embedding function based on configuration.
    """
    if USE_EMBEDDING_PROVIDER == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set but is required for Google embeddings.")
        
        genai.configure(api_key=GEMINI_API_KEY)
        return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    elif USE_EMBEDDING_PROVIDER == "local":
        print(f"Using local embedding model: {LOCAL_EMBEDDING_MODEL}")
        return HuggingFaceEmbeddings(
            model_name=LOCAL_EMBEDDING_MODEL,
            cache_folder=str(MODELS_CACHE_DIR / "embeddings"),
            encode_kwargs={'normalize_embeddings': True}
        )
    
    else:  # Default to OpenAI
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set but is required for OpenAI embeddings.")
        
        return OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY, 
            model="text-embedding-ada-002"
        )

def main():
    try:
        if not SUBTITLES_FOLDER.exists():
            print(f"Folder '{SUBTITLES_FOLDER}' does not exist.")
            return
        
        srt_files = list(SUBTITLES_FOLDER.glob("*.srt"))
        if not srt_files:
            print("No SRT files found to process.")
            return
        
        print(f"Found {len(srt_files)} SRT files to process")
        
        # Process files sequentially (faster for small numbers)
        all_subtitles = []
        for file in srt_files:
            print(f"Processing: {file.name}")
            subtitles = parse_srt_file(file)
            all_subtitles.extend(subtitles)
            print(f"  -> {len(subtitles)} entries")
        
        if not all_subtitles:
            print("No subtitles found to process.")
            return
        
        print(f"Total processed: {len(all_subtitles)} subtitle entries")
        
        # Save metadata
        metadata = pd.DataFrame(all_subtitles)
        metadata.to_csv(METADATA_FILE, index=False)
        print(f"Saved metadata to {METADATA_FILE}")

        # Prepare documents for ChromaDB
        print("Creating documents for vector database...")
        documents = [
            Document(
                page_content=item["text"], 
                metadata={
                    "video_id": item["video_id"],
                    "start_time": item["start_time"],
                    "timestamp": item["timestamp"],
                    "link": item["link"]
                }
            )
            for item in all_subtitles
        ]

        # Get embedding function
        embedding_fn = get_embedding_function()
        print(f"Using embedding provider: {USE_EMBEDDING_PROVIDER}")
        
        # Create/update ChromaDB
        print("Creating vector database...")
        if CHROMA_DB_DIRECTORY.exists() and any(CHROMA_DB_DIRECTORY.iterdir()):
            print("Updating existing Chroma database...")
            subtitlesdb = Chroma(
                persist_directory=str(CHROMA_DB_DIRECTORY), 
                embedding_function=embedding_fn
            )
            subtitlesdb.add_documents(documents)
        else:
            print("Creating a new Chroma database...")
            subtitlesdb = Chroma.from_documents(
                documents=documents,
                embedding=embedding_fn,
                persist_directory=str(CHROMA_DB_DIRECTORY)
            )
        
        print("✅ Data successfully saved to Chroma DB.")

        # Clean up processed files
        for srt_file in srt_files:
            try:
                srt_file.unlink()
                print(f"Deleted file: {srt_file.name}")
            except Exception as e:
                print(f"Could not delete file {srt_file.name}: {e}")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()