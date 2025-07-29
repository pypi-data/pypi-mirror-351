import re
import urllib.parse
from typing import Optional, List, Dict
from functools import lru_cache

# Compiled regex patterns for better performance
YOUTUBE_ID_PATTERNS = [
    # Standard youtube.com watch URLs
    re.compile(r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})'),
    
    # Short youtu.be URLs
    re.compile(r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})'),
    
    # Embedded URLs
    re.compile(r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})'),
    
    # YouTube mobile URLs
    re.compile(r'(?:m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})'),
    
    # YouTube with additional parameters
    re.compile(r'(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})'),
    
    # YouTube playlist URLs (extract video ID)
    re.compile(r'(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})(?:.*&list=)'),
    
    # YouTube shorts URLs
    re.compile(r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})'),
]

# Channel URL patterns
CHANNEL_PATTERNS = [
    re.compile(r'youtube\.com/c/([^/?&]+)'),
    re.compile(r'youtube\.com/channel/([^/?&]+)'),
    re.compile(r'youtube\.com/user/([^/?&]+)'),
    re.compile(r'youtube\.com/@([^/?&]+)'),
]

@lru_cache(maxsize=1000)
def extract_video_id(url: str) -> Optional[str]:
    """
    Optimized video ID extraction with caching and multiple URL format support.
    
    Supports:
    - youtube.com/watch?v=VIDEO_ID
    - youtu.be/VIDEO_ID
    - youtube.com/embed/VIDEO_ID
    - m.youtube.com/watch?v=VIDEO_ID
    - youtube.com/shorts/VIDEO_ID
    - URLs with additional parameters
    
    Args:
        url: YouTube URL string
        
    Returns:
        11-character video ID or None if not found
    """
    if not url or not isinstance(url, str):
        return None
    
    # Clean and normalize URL
    url = url.strip()
    
    # Handle URLs without protocol
    if not url.startswith(('http://', 'https://')):
        if url.startswith('youtu.be/') or url.startswith('youtube.com/'):
            url = 'https://' + url
        else:
            return None
    
    # Try each pattern
    for pattern in YOUTUBE_ID_PATTERNS:
        match = pattern.search(url)
        if match:
            video_id = match.group(1)
            # Validate video ID format (11 characters, alphanumeric + _ -)
            if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return video_id
    
    # Fallback: try urllib.parse for complex URLs
    try:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        if 'v' in query_params and query_params['v']:
            video_id = query_params['v'][0]
            if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return video_id
    except Exception:
        pass
    
    return None

def extract_video_ids_batch(urls: List[str]) -> List[Optional[str]]:
    """
    Extract video IDs from multiple URLs efficiently.
    
    Args:
        urls: List of YouTube URL strings
        
    Returns:
        List of video IDs (same order as input, None for invalid URLs)
    """
    return [extract_video_id(url) for url in urls]

def extract_channel_info(url: str) -> Optional[Dict[str, str]]:
    """
    Extract channel information from YouTube channel URLs.
    
    Args:
        url: YouTube channel URL
        
    Returns:
        Dict with channel type and ID, or None if not a channel URL
    """
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    # Handle URLs without protocol
    if not url.startswith(('http://', 'https://')):
        if url.startswith('youtube.com/'):
            url = 'https://' + url
        else:
            return None
    
    for pattern in CHANNEL_PATTERNS:
        match = pattern.search(url)
        if match:
            channel_id = match.group(1)
            
            if 'youtube.com/c/' in url:
                return {'type': 'custom', 'id': channel_id}
            elif 'youtube.com/channel/' in url:
                return {'type': 'channel', 'id': channel_id}
            elif 'youtube.com/user/' in url:
                return {'type': 'user', 'id': channel_id}
            elif 'youtube.com/@' in url:
                return {'type': 'handle', 'id': channel_id}
    
    return None

def is_youtube_url(url: str) -> bool:
    """
    Fast check if URL is a YouTube URL.
    
    Args:
        url: URL string to check
        
    Returns:
        True if it's a YouTube URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.lower().strip()
    
    youtube_domains = [
        'youtube.com',
        'youtu.be',
        'm.youtube.com',
        'www.youtube.com'
    ]
    
    return any(domain in url for domain in youtube_domains)

def is_video_url(url: str) -> bool:
    """
    Check if URL is specifically a YouTube video URL.
    
    Args:
        url: URL string to check
        
    Returns:
        True if it's a YouTube video URL, False otherwise
    """
    return extract_video_id(url) is not None

def is_channel_url(url: str) -> bool:
    """
    Check if URL is a YouTube channel URL.
    
    Args:
        url: URL string to check
        
    Returns:
        True if it's a YouTube channel URL, False otherwise
    """
    return extract_channel_info(url) is not None

def clean_youtube_url(url: str) -> Optional[str]:
    """
    Clean and normalize YouTube URL by removing unnecessary parameters.
    
    Args:
        url: YouTube URL to clean
        
    Returns:
        Cleaned URL or None if invalid
    """
    video_id = extract_video_id(url)
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    
    channel_info = extract_channel_info(url)
    if channel_info:
        if channel_info['type'] == 'handle':
            return f"https://www.youtube.com/@{channel_info['id']}"
        elif channel_info['type'] == 'channel':
            return f"https://www.youtube.com/channel/{channel_info['id']}"
        elif channel_info['type'] == 'custom':
            return f"https://www.youtube.com/c/{channel_info['id']}"
        elif channel_info['type'] == 'user':
            return f"https://www.youtube.com/user/{channel_info['id']}"
    
    return None

def validate_video_id(video_id: str) -> bool:
    """
    Validate if a string is a valid YouTube video ID.
    
    Args:
        video_id: String to validate
        
    Returns:
        True if valid video ID, False otherwise
    """
    if not video_id or not isinstance(video_id, str):
        return False
    
    return len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id) is not None

def get_url_info(url: str) -> Dict[str, any]:
    """
    Get comprehensive information about a YouTube URL.
    
    Args:
        url: YouTube URL to analyze
        
    Returns:
        Dict with URL type, ID, and other info
    """
    result = {
        'is_youtube': is_youtube_url(url),
        'is_video': False,
        'is_channel': False,
        'video_id': None,
        'channel_info': None,
        'clean_url': None,
        'original_url': url
    }
    
    if not result['is_youtube']:
        return result
    
    # Check for video
    video_id = extract_video_id(url)
    if video_id:
        result['is_video'] = True
        result['video_id'] = video_id
        result['clean_url'] = f"https://www.youtube.com/watch?v={video_id}"
    
    # Check for channel
    channel_info = extract_channel_info(url)
    if channel_info:
        result['is_channel'] = True
        result['channel_info'] = channel_info
        
        if channel_info['type'] == 'handle':
            result['clean_url'] = f"https://www.youtube.com/@{channel_info['id']}"
        elif channel_info['type'] == 'channel':
            result['clean_url'] = f"https://www.youtube.com/channel/{channel_info['id']}"
    
    return result

# For backward compatibility
def extract_video_id_legacy(url: str) -> Optional[str]:
    """
    Legacy function for backward compatibility.
    Same as extract_video_id but without caching.
    """
    return extract_video_id.__wrapped__(url) if hasattr(extract_video_id, '__wrapped__') else extract_video_id(url)
