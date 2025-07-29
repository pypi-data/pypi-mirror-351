import os
import gradio as gr
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import time

SCRIPT_DIR = Path(__file__).parent
SRC_DIR = SCRIPT_DIR / "src"

load_dotenv(".env")

def is_url(text: str) -> bool:
    """
    Checks if the user passes a YouTube url to process or not.
    """
    return text.startswith("https://www.youtube.com") or text.startswith("https://youtu.be")

def update_provider_config(provider_choice: str):
    """
    Update environment variables based on provider choice
    """
    if provider_choice == "OpenAI (Cloud)":
        os.environ["USE_EMBEDDING_PROVIDER"] = "openai"
        os.environ["USE_LLM_PROVIDER"] = "openai"
        return "✅ Provider set to OpenAI"
    elif provider_choice == "Google (Cloud)":
        os.environ["USE_EMBEDDING_PROVIDER"] = "google"
        os.environ["USE_LLM_PROVIDER"] = "google"
        return "✅ Provider set to Google"
    elif provider_choice == "Local Models":
        os.environ["USE_EMBEDDING_PROVIDER"] = "local"
        os.environ["USE_LLM_PROVIDER"] = "local"
        return "✅ Provider set to Local Models"
    return "Provider updated"

def process_video(video_url: str, provider_choice: str):
    """
    Process YouTube video or channel URL
    """
    if not video_url or not video_url.strip():
        return "❌ Please enter a YouTube URL", ""

    video_url = video_url.strip()
    
    if not is_url(video_url):
        return "❌ Please enter a valid YouTube URL", ""

    # Update provider
    update_provider_config(provider_choice)
    
    try:
        # Call parser.py to process the link
        result = subprocess.run(
            ["python3", str(SRC_DIR / "parser.py"), video_url], 
            capture_output=True, 
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
            return f"❌ Error parsing URL: {error_msg}", ""

        # Call create_database.py to update the database
        result = subprocess.run(
            ["python3", str(SRC_DIR / "create_database.py")], 
            capture_output=True, 
            text=True,
            timeout=180
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
            return f"❌ Error updating database: {error_msg}", ""

        success_msg = "✅ Video processed successfully and added to database"
        return success_msg, ""  # Clear the input field

    except subprocess.TimeoutExpired:
        return "❌ Operation timed out. Try with fewer videos or check your connection.", video_url
    except Exception as e:
        return f"❌ Error processing video: {str(e)}", video_url

def search_videos(query: str, provider_choice: str):
    """
    Search the video database
    """
    if not query or not query.strip():
        return "Please enter a search query"

    query = query.strip()
    
    # Update provider
    update_provider_config(provider_choice)
    
    try:
        # Call query.py to search the database
        result = subprocess.run(
            ["python3", str(SRC_DIR / "query.py"), query], 
            capture_output=True, 
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
            return f"❌ Error searching database: {error_msg}"
        
        response = result.stdout.strip()
        if not response:
            return "No results found. Try rephrasing your query or add more videos to the database."
        
        return response

    except subprocess.TimeoutExpired:
        return "❌ Search timed out. Try a simpler query."
    except Exception as e:
        return f"❌ Error during search: {str(e)}"

def main():
    # Custom CSS for clean white design
    css = """
    .gradio-container {
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    
    .main-header {
        text-align: center;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 30px;
        color: #333;
    }
    
    .section-container {
        margin-bottom: 25px;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: white;
    }
    
    .section-title {
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 15px;
        color: #333;
    }
    
    .input-row {
        display: flex;
        gap: 10px;
    }
    
    .process-status {
        margin-top: 10px;
        padding: 10px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .results-container {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #eee;
        border-radius: 6px;
        padding: 15px;
        background: #fafafa;
    }
    """
    
    with gr.Blocks(css=css, title="YouTube Video Search Tool") as demo:
        
        # Title
        gr.HTML('<h1 class="main-header">YouTube Video Search Tool</h1>')
        
        # Provider Selection Section
        with gr.Group():
            gr.HTML('<div class="section-title">Choose AI Provider</div>')
            provider_dropdown = gr.Dropdown(
                choices=["OpenAI (Cloud)", "Google (Cloud)", "Local Models"],
                value="OpenAI (Cloud)",
                show_label=False,
                container=False
            )
        
        # Video Processing Section  
        with gr.Group():
            gr.HTML('<div class="section-title">Add YouTube Video or Channel</div>')
            
            with gr.Row():
                video_input = gr.Textbox(
                    placeholder="Paste YouTube video URL or channel URL here...",
                    show_label=False,
                    scale=4,
                    container=False
                )
                process_btn = gr.Button(
                    "Process", 
                    variant="primary",
                    scale=1,
                    size="sm"
                )
            
            process_status = gr.Textbox(
                show_label=False,
                container=False,
                interactive=False,
                placeholder="Ready to process videos"
            )
        
        # Search Section
        with gr.Group():
            gr.HTML('<div class="section-title">Search Videos</div>')
            
            with gr.Row():
                query_input = gr.Textbox(
                    placeholder="Enter your search query (e.g., 'machine learning', 'python tutorial')...",
                    show_label=False,
                    scale=4,
                    container=False
                )
                search_btn = gr.Button(
                    "Search",
                    variant="primary", 
                    scale=1,
                    size="sm"
                )
        
        # Results Section
        with gr.Group():
            gr.HTML('<div class="section-title">Search Results (Top 3 Matches)</div>')
            results_output = gr.Textbox(
                value="No search results yet. Add some videos and try searching!",
                show_label=False,
                lines=15,
                max_lines=20,
                container=False,
                interactive=False,
                elem_classes=["results-container"]
            )
        
        # Event handlers
        process_btn.click(
            fn=process_video,
            inputs=[video_input, provider_dropdown],
            outputs=[process_status, video_input]
        )
        
        search_btn.click(
            fn=search_videos,
            inputs=[query_input, provider_dropdown],
            outputs=[results_output]
        )
        
        # Allow Enter key functionality
        video_input.submit(
            fn=process_video,
            inputs=[video_input, provider_dropdown],
            outputs=[process_status, video_input]
        )
        
        query_input.submit(
            fn=search_videos,
            inputs=[query_input, provider_dropdown],
            outputs=[results_output]
        )

    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()