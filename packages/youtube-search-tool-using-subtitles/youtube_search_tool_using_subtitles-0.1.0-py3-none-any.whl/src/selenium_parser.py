import time
import re
import os
from typing import Set, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

MAX_VIDEOS = int(os.getenv("MAX_CHANNEL_VIDEOS", "100"))
SCROLL_PAUSE_TIME = float(os.getenv("SCROLL_PAUSE_TIME", "2.0"))
MAX_SCROLLS = int(os.getenv("MAX_SCROLLS", "10"))
HEADLESS = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"


def create_optimized_driver() -> webdriver.Chrome:
    """
    Create an optimized Chrome driver with performance settings
    """
    chrome_options = Options()
    
    if HEADLESS:
        chrome_options.add_argument("--headless")
    
    # Performance optimizations
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Disable images, CSS, and JavaScript for faster loading
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
    })
    
    # Memory and CPU optimizations
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # User agent to avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"Error creating Chrome driver: {e}")
        print("Please ensure ChromeDriver is installed and in PATH")
        raise

def handle_cookie_consent(driver: webdriver.Chrome) -> bool:
    """
    Handle cookie consent popup more reliably
    """
    try:
        # Wait for page to stabilize
        time.sleep(3)
        
        # Try multiple selectors for cookie consent
        consent_selectors = [
            "//button[contains(text(), 'Reject all')]",
            "//button[contains(text(), 'Accept all')]", 
            "//button[@aria-label='Reject all']",
            "//button[@aria-label='Accept all']",
            "//button[contains(@class, 'yt-spec-button-shape-next--call-to-action')]//span[contains(text(), 'Accept')]",
            "//*[@id='dialog']//button[contains(text(), 'OK')]"
        ]
        
        for selector in consent_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                button.click()
                print("✓ Cookie consent handled")
                time.sleep(2)
                return True
            except TimeoutException:
                continue
        
        print("ℹ No cookie consent popup found or already handled")
        return True
        
    except Exception as e:
        print(f"⚠ Cookie consent handling failed: {e}")
        return False

def smart_scroll_and_extract(driver: webdriver.Chrome, max_videos: int = MAX_VIDEOS) -> Set[str]:
    """
    Intelligently scroll and extract video links with early stopping
    """
    video_urls = set()
    last_count = 0
    consecutive_no_new = 0
    scroll_count = 0
    
    print(f"🔄 Starting to extract videos (max: {max_videos})")
    
    while scroll_count < MAX_SCROLLS and len(video_urls) < max_videos:
        # Extract current video links
        try:
            # More specific selector to avoid shorts and other non-video content
            video_elements = driver.find_elements(
                By.XPATH, 
                "//a[@id='video-title-link' or contains(@href, '/watch?v=')][@href]"
            )
            
            for element in video_elements:
                href = element.get_attribute('href')
                if href and '/watch?v=' in href and href not in video_urls:
                    # Clean the URL (remove playlist and other parameters)
                    clean_url = href.split('&list=')[0].split('&index=')[0]
                    video_urls.add(clean_url)
                    
                    if len(video_urls) >= max_videos:
                        print(f"✓ Reached maximum videos limit ({max_videos})")
                        break
            
        except Exception as e:
            print(f"⚠ Error extracting videos: {e}")
        
        current_count = len(video_urls)
        print(f"📊 Found {current_count} videos (scroll {scroll_count + 1})")
        
        # Check if we're still finding new videos
        if current_count == last_count:
            consecutive_no_new += 1
            if consecutive_no_new >= 3:
                print("🛑 No new videos found in last 3 scrolls, stopping")
                break
        else:
            consecutive_no_new = 0
        
        last_count = current_count
        
        # Scroll down
        try:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            
            # Check if we've reached the end
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if scroll_count > 0:
                old_height = driver.execute_script("return window.pageYOffset + window.innerHeight")
                if old_height >= new_height * 0.95:
                    print("📄 Reached end of page")
                    break
                    
        except Exception as e:
            print(f"⚠ Scroll error: {e}")
            
        scroll_count += 1
    
    print(f"✅ Extraction complete: {len(video_urls)} videos found")
    return video_urls

def extract_video_links_from_html(html_content: str) -> Set[str]:
    """
    Fast regex-based extraction as backup method
    """
    # Pattern to match YouTube video URLs
    pattern = re.compile(r'href="(/watch\?v=[a-zA-Z0-9_-]{11}[^"]*)"')
    matches = pattern.findall(html_content)
    
    video_urls = set()
    for href in matches:
        # Clean and construct full URL
        clean_href = href.split('&list=')[0].split('&index=')[0]
        full_url = f"https://www.youtube.com{clean_href}"
        video_urls.add(full_url)
    
    return video_urls

def cache_results(channel_url: str, video_urls: List[str]) -> None:
    """
    Cache results to avoid re-scraping the same channel
    """
    try:
        cache_dir = Path(__file__).parent.parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        
        cache_file = cache_dir / f"channel_{hash(channel_url) % 10000}.json"
        
        cache_data = {
            "channel_url": channel_url,
            "video_urls": list(video_urls),
            "timestamp": time.time(),
            "count": len(video_urls)
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
            
        print(f"💾 Results cached to {cache_file.name}")
        
    except Exception as e:
        print(f"⚠ Caching failed: {e}")

def load_cached_results(channel_url: str, max_age_hours: int = 24) -> List[str]:
    """
    Load cached results if they exist and are recent
    """
    try:
        cache_dir = Path(__file__).parent.parent / "cache"
        cache_file = cache_dir / f"channel_{hash(channel_url) % 10000}.json"
        
        if not cache_file.exists():
            return []
        
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Check if cache is recent enough
        age_hours = (time.time() - cache_data['timestamp']) / 3600
        if age_hours > max_age_hours:
            print(f"⏰ Cache expired ({age_hours:.1f}h old), re-scraping")
            return []
        
        print(f"📋 Using cached results ({cache_data['count']} videos, {age_hours:.1f}h old)")
        return cache_data['video_urls']
        
    except Exception as e:
        print(f"⚠ Cache loading failed: {e}")
        return []

def scrape_channel_videos(channel_url: str, use_cache: bool = True) -> List[str]:
    """
    Main function to scrape channel videos with optimizations
    """
    start_time = time.time()
    print(f"🎯 Scraping channel: {channel_url}")
    
    # Check cache first
    if use_cache:
        cached_results = load_cached_results(channel_url)
        if cached_results:
            return cached_results
    
    driver = None
    try:
        # Create optimized driver
        driver = create_optimized_driver()
        print("🚀 Chrome driver created successfully")
        
        # Navigate to channel
        print("🌐 Loading channel page...")
        driver.get(channel_url)
        
        # Handle cookie consent
        handle_cookie_consent(driver)
        
        # Wait for page to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "ytd-rich-grid-media"))
            )
        except TimeoutException:
            print("⚠ Page load timeout, trying anyway...")
        
        # Extract video URLs using smart scrolling
        video_urls = smart_scroll_and_extract(driver, MAX_VIDEOS)
        
        # Fallback: extract from current page HTML
        if len(video_urls) < 5:
            print("🔄 Using fallback HTML extraction...")
            html_content = driver.page_source
            fallback_urls = extract_video_links_from_html(html_content)
            video_urls.update(fallback_urls)
        
        video_list = list(video_urls)
        
        # Cache results
        if video_list and use_cache:
            cache_results(channel_url, video_list)
        
        elapsed = time.time() - start_time
        print(f"✅ Scraping completed in {elapsed:.1f}s - Found {len(video_list)} videos")
        
        return video_list
        
    except WebDriverException as e:
        print(f"❌ WebDriver error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
                print("🔒 Browser closed")
            except Exception as e:
                print(f"⚠ Error closing browser: {e}")

if __name__ == "__main__":
    # Test the scraper
    test_url = "https://www.youtube.com/@3blue1brown/videos"
    videos = scrape_channel_videos(test_url)
    print(f"Test result: {len(videos)} videos found")
    for i, video in enumerate(videos[:5], 1):
        print(f"{i}. {video}")