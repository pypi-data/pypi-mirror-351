import sys
import urllib.parse
import time
import os
from typing import List

from get_subs import main as get_subs_main, extract_video_id, download_subtitles_batch
from selenium_parser import scrape_channel_videos

# Get max workers from environment
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))

def is_channel_url(url: str) -> bool:
    """
    Checks if the URL likely corresponds to a channel page or is it a single video link
    """
    url_lower = url.lower()
    channel_markers = ("@", "/channel/", "/c/", "/user/")
    if any(m in url_lower for m in channel_markers):
        return True 
    return False

def fix_url(url: str) -> str:
    """
    If the passed channel url is not for the videos but for other pages 
    this function changes it and returns an URL ending in /videos.
    """
    parsed = urllib.parse.urlparse(url)
    path_parts = parsed.path.split("/")

    excluded_segments = {"featured", "shorts", "streams", "community", "playlists", "store", ""}
    while len(path_parts) > 1 and path_parts[-1].lower() in excluded_segments:
        path_parts.pop()

    if path_parts[-1].lower() != "videos":
        path_parts.append("videos")

    new_path = "/".join(path_parts)
    fixed_url = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        new_path,
        "",  # params
        "",  # query
        ""   # fragment
    ))

    return fixed_url

def process_single_video(youtube_url: str) -> bool:
    """
    Process a single video URL
    """
    print("Detected single video URL.")
    video_id = extract_video_id(youtube_url)

    if video_id:
        print(f"Extracting subtitles for video_id={video_id}")
        get_subs_main(video_id=video_id)
        return True
    else:
        print("Could not extract a valid video ID from the provided URL.")
        return False

def process_channel(youtube_url: str) -> bool:
    """
    Process a channel URL with optimized batch processing
    """
    channel_url = fix_url(youtube_url)
    print(f"Detected channel URL. Scraping {channel_url}...")
    
    try:
        video_links = scrape_channel_videos(channel_url)
        print(f"Found {len(video_links)} videos on the channel.")
        
        if not video_links:
            print("No videos found on the channel.")
            return False
        
        # Extract video IDs
        video_ids = []
        for link in video_links:
            video_id = extract_video_id(link)
            if video_id:
                video_ids.append(video_id)
            else:
                print(f"Skipping invalid link: {link}")
        
        if not video_ids:
            print("No valid video IDs found.")
            return False
        
        print(f"Processing {len(video_ids)} videos with {MAX_WORKERS} workers...")
        
        # Use batch processing 
        results = download_subtitles_batch(video_ids, max_workers=MAX_WORKERS)
        
        successful = sum(1 for success in results.values() if success)
        print(f"Successfully processed {successful}/{len(video_ids)} videos")
        
        return successful > 0
        
    except Exception as e:
        print(f"Error processing channel: {e}")
        return False

def main():
    start_time = time.time()
    
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1].strip()
    else:
        youtube_url = input("Enter a YouTube URL to a single video or a channel: ").strip()
    
    if not youtube_url:
        print("No URL provided.")
        return
    
    success = False
    
    try:
        if is_channel_url(youtube_url):
            success = process_channel(youtube_url)
        else:
            success = process_single_video(youtube_url)
    
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    
    end_time = time.time()
    total_time = end_time - start_time
    minutes = int(total_time) // 60
    seconds = int(total_time) % 60
    
    status = "✅ Completed" if success else "❌ Failed"
    print(f"\n{status} - Total time: {minutes}m {seconds}s")

if __name__ == "__main__":
    main()