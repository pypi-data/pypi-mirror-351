# YouTube Search Tool

Search and query YouTube videos using AI embeddings. Add individual videos or entire channels, then search through their content using natural language.

## Features

- 🎥 Process individual YouTube videos or entire channels
- 🔍 Semantic search through video transcripts  
- 🤖 Multiple AI providers (OpenAI, Google, Local models)
- 🌐 Web interface with Gradio
- ⚡ Fast batch processing with concurrent downloads

## Installation

```bash
pip install youtube-search-tool
```

## Quick Start

### 1. Set up environment
Create a `.env` file:
```bash
# Choose your AI provider
USE_EMBEDDING_PROVIDER=openai  # or 'google' or 'local'
USE_LLM_PROVIDER=openai

# API Keys (if using cloud providers)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_google_key

# Optional: Customize processing
MAX_WORKERS=4
MAX_CHANNEL_VIDEOS=100
```

### 2. Add videos
```bash
# Add a single video
yt-search add "https://www.youtube.com/watch?v=QPM0WNqwJBc"

# Add an entire channel
yt-search add "https://www.youtube.com/@Lamediainglesa"
```

### 3. Search
```bash
# Search through your videos
yt-search search "machine learning basics"
yt-search search "python tutorial"
```

### 4. Web Interface
```bash
# Launch the web interface
yt-search web
```

## Requirements

- Python 3.8+
- Chrome/Chromium browser (for channel scraping)
- API keys for cloud providers (optional, can use local models)

## Supported AI Providers

- **OpenAI**: `text-embedding-ada-002` (requires API key)
- **Google**: `text-embedding-004` (requires API key)  
- **Local**: `all-MiniLM-L6-v2` (no API key needed)

## License

MIT License