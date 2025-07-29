import sys
import subprocess
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent  
SRC_DIR = SCRIPT_DIR / "src"

def run_parser(url):
    """Add a YouTube video or channel"""
    try:
        result = subprocess.run(
            [sys.executable, str(SRC_DIR / "parser.py"), url],
            check=True
        )
        
        # Run database creation after parsing
        subprocess.run(
            [sys.executable, str(SRC_DIR / "create_database.py")],
            check=True
        )
        
        print("✅ Video/channel added successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def run_search(query):
    """Search the video database"""
    try:
        result = subprocess.run(
            [sys.executable, str(SRC_DIR / "query.py"), query],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def run_web():
    """Launch the web interface"""
    try:
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "gradio_app.py")],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Search Tool - Search and query YouTube videos using AI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a YouTube video or channel")
    add_parser.add_argument("url", help="YouTube URL (video or channel)")
    
    # Search command  
    search_parser = subparsers.add_parser("search", help="Search the video database")
    search_parser.add_argument("query", help="Search query")
    
    # Web command
    web_parser = subparsers.add_parser("web", help="Launch web interface")
    
    args = parser.parse_args()
    
    if args.command == "add":
        run_parser(args.url)
    elif args.command == "search":
        run_search(args.query)
    elif args.command == "web":
        run_web()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()