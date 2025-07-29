from youtube_transcript_api import YouTubeTranscriptApi
import math
import os
import sys
import urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import time

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

def float_to_str_time(t: float) -> str:
    """ 
    Transforms time into a string 
    """
    seconds = int(math.floor(t))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def save_subtitles(transcript: List, output_path: str, video_id: str):
    """
    Saves subtitles as srt file with optimized format
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for index, entry in enumerate(transcript, start=1):
                # The transcript entries are now objects, not dictionaries
                start_time = float_to_str_time(entry.start)
                end_time = float_to_str_time(entry.start + entry.duration)
                start_seconds = int(math.floor(entry.start))
                text = entry.text.replace('\n', ' ').strip()

                f.write(f"{index}\n")
                f.write(f"{start_time} --> {end_time} ({start_seconds})\n")
                f.write(f"{text}\n\n")
        
        return True
    except Exception as e:
        print(f"Error saving subtitles for {video_id}: {e}")
        print(f"Entry type: {type(transcript[0]) if transcript else 'No transcript'}")
        if transcript:
            print(f"First entry: {transcript[0]}")
        return False

def extract_video_id(url: str) -> str:
    """
    Extract the 'v=' parameter from a YouTube watch URL.
    Supports both youtube.com and youtu.be formats
    """
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    if 'v' in query_params and len(query_params['v']) > 0:
        return query_params['v'][0]
    
    return None

def download_subtitles_for_video(video_id: str, output_folder: Path) -> bool:
    """
    Download subtitles for a single video with improved error handling
    """
    import time
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} for video {video_id}")
            
            # Get transcript list
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Debug: Print available languages
            print(f"Available transcripts for {video_id}:")
            available_languages = []
            for transcript in transcript_list:
                print(f"  - {transcript.language} ({transcript.language_code})")
                available_languages.append(transcript.language_code)
            
            # Try to get transcript in preferred order
            transcript = transcript_list.find_transcript(['ru', 'en', 'es', 'de', 'fr']).fetch()
            
            print(f"✓ Downloaded {len(transcript)} transcript entries")
            if transcript:
                print(f"First entry: {transcript[0].text[:50]}...")
            
            output_file = output_folder / f"{video_id}.srt"
            success = save_subtitles(transcript, str(output_file), video_id)
            
            if success:
                print(f"✓ Subtitles saved: {video_id}")
                return True
            else:
                print(f"✗ Failed to save: {video_id}")
                return False
                
        except Exception as e:
            print(f"✗ Attempt {attempt + 1} failed for {video_id}: {e}")
            
            if "ParseError" in str(e) or "no element found" in str(e):
                print("  XML Parse error - possibly network issue or temporary unavailability")
            elif "NoTranscriptFound" in str(e):
                print("  No transcript available in requested languages")
                return False
            elif "TranscriptsDisabled" in str(e):
                print("  Transcripts are disabled for this video")
                return False
            elif "VideoUnavailable" in str(e):
                print("  Video is unavailable")
                return False
            
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"  All {max_retries} attempts failed")
                import traceback
                traceback.print_exc()
                return False
    
    return False

def download_subtitles_batch(video_ids: List[str], max_workers: int = 4) -> Dict[str, bool]:
    """
    Download subtitles for multiple videos concurrently
    """
    output_folder = PROJECT_ROOT / "subtitles"
    output_folder.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_video = {
            executor.submit(download_subtitles_for_video, video_id, output_folder): video_id 
            for video_id in video_ids
        }
        
        for future in as_completed(future_to_video):
            video_id = future_to_video[future]
            try:
                success = future.result()
                results[video_id] = success
            except Exception as e:
                print(f"Error processing {video_id}: {e}")
                results[video_id] = False
    
    return results

def main(video_id: str = None, video_ids: List[str] = None):
    """
    Main function supporting both single video and batch processing
    """
    start_time = time.time()
    
    if video_ids:
        # Batch processing
        print(f"Downloading subtitles for {len(video_ids)} videos...")
        results = download_subtitles_batch(video_ids)
        
        successful = sum(1 for success in results.values() if success)
        print(f"\n📊 Results: {successful}/{len(video_ids)} videos processed successfully")
        
        if successful < len(video_ids):
            failed_videos = [vid for vid, success in results.items() if not success]
            print(f"Failed videos: {failed_videos}")
    
    elif video_id:
        # Single video processing
        output_folder = PROJECT_ROOT / "subtitles"
        output_folder.mkdir(parents=True, exist_ok=True)
        
        success = download_subtitles_for_video(video_id, output_folder)
        if success:
            print(f"Subtitles successfully saved for video: {video_id}")
        else:
            print(f"Failed to download subtitles for video: {video_id}")
    
    else:
        print("No video ID(s) provided")
        return
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"⏱️  Total time: {duration:.2f} seconds")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_id_argv = sys.argv[1]
        main(video_id=video_id_argv)
    else:
        video_id_input = input("Enter the YouTube video ID: ").strip()
        if video_id_input:
            main(video_id=video_id_input)
        else:
            print("No video ID provided")