import requests
import random
import logging
from django.db import IntegrityError
from datetime import datetime, timedelta
from .models import ImageURL
from pinterest_dl import PinterestDL
from dotenv import load_dotenv
import os
import json
import time

logger = logging.getLogger(__name__)

class ImageURLManager:
    """Helper class to manage ImageURL database operations"""
    
    @staticmethod
    def add_urls(urls, source='unknown'):
        """Add new URLs to database, returns count of added URLs"""
        if not urls:
            return 0
        
        image_instances = []
        for url_data in urls:
            if isinstance(url_data, dict):
                image_instances.append(ImageURL(
                    src=url_data.get('src', ''),
                    alt=url_data.get('alt', ''),
                    origin=url_data.get('origin', source),
                    fallback_urls=url_data.get('fallback_urls', [])
                ))
            else:
                # Handle simple string URLs
                image_instances.append(ImageURL(
                    src=str(url_data),
                    alt='',
                    origin=source,
                    fallback_urls=[]
                ))
        
        if image_instances:
            ImageURL.objects.bulk_create(image_instances, ignore_conflicts=True)
            return len(image_instances)
        return 0
    
    @staticmethod
    def get_random_urls(count=10):
        """Get random active URLs from database"""
        active_images = ImageURL.objects.filter(is_active=True)
        
        if not active_images.exists():
            return []
        
        # Get random selection
        if active_images.count() <= count:
            return list(active_images)
        else:
            return list(active_images.order_by('?')[:count])  # Random order
    
    @staticmethod
    def get_active_count():
        """Get count of active URLs in database"""
        return ImageURL.objects.filter(is_active=True).count()
    
    @staticmethod
    def deactivate_old_urls(days=30):
        """Deactivate URLs older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        updated_count = ImageURL.objects.filter(
            created_at__lt=cutoff_date,
            is_active=True
        ).update(is_active=False)
        return updated_count

class ImageScrapingService:
    def __init__(self):
        self.url_manager = ImageURLManager()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_home_images(self, count=20):
        """Scrape images from Pinterest home feed - automated for cron tasks"""
        try:
            # first check if we have cookies (automated, no user interaction)
            if not get_valid_pinterest_cookies():
                logger.error("Failed to get valid Pinterest cookies")
                return {
                    'success': False,
                    'message': 'No valid cookies found',
                    'new_images_count': 0,
                    'total_images': 0
                }
            
            # download the images
            download_home_feed()
            
            # Get current count from database
            total_images = ImageURL.objects.count()
            
            # For now, we'll return success - in the future we can track new vs existing
            return {
                'success': True,
                'message': 'Images downloaded successfully',
                'new_images_count': count,  # placeholder - will be accurate once we implement proper tracking
                'total_images': total_images
            }
            
        except Exception as e:
            logger.error(f"Error in scrape_home_images: {e}")
            return {
                'success': False,
                'message': f'Scraping failed: {str(e)}',
                'new_images_count': 0,
                'total_images': 0
            }
        


def check_cookies_expired(cookies_path):
    """
    Check if Pinterest cookies are expired
    Returns: (exists, expired, time_remaining_hours)
    """
    if not os.path.exists(cookies_path):
        return False, True, 0  # File doesn't exist, consider expired
    
    try:
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
        
        if not cookies:
            return True, True, 0  # Empty cookies file, consider expired
        
        current_time = int(time.time())
        min_expiry = float('inf')
        
        # Find the cookie with the earliest expiry time
        for cookie in cookies:
            if 'expiry' in cookie:
                min_expiry = min(min_expiry, cookie['expiry'])
        
        if min_expiry == float('inf'):
            return True, True, 0  # No expiry found, consider expired
        
        expired = current_time >= min_expiry
        time_remaining_seconds = max(0, min_expiry - current_time)
        time_remaining_hours = time_remaining_seconds / 3600
        
        return True, expired, time_remaining_hours
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"❌ Error reading cookies file: {e}")
        return True, True, 0  # Error reading file, consider expired


def get_pinterest_cookies_python(force_refresh=False, automated=False):
    """
    Smart Pinterest cookie management
    Checks for existing cookies and their expiry before fetching new ones
    
    Args:
        force_refresh (bool): If True, forces new cookie fetch regardless of expiry
        automated (bool): If True, runs in fully automated mode (no user interaction, headless)
    
    Returns:
        bool: True if cookies are available and valid, False otherwise
    """
    if not automated:
        print("\n🔑 Smart Pinterest Cookie Manager")
        print("=" * 50)
    
    # Get cookies file path
    cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.json")
    
    # Check existing cookies first
    exists, expired, time_remaining = check_cookies_expired(cookies_path)
    
    if exists and not expired and not force_refresh:
        if not automated:
            print(f"✅ Valid cookies found!")
            print(f"📁 Cookie file: {cookies_path}")
            print(f"⏰ Time remaining: {time_remaining:.1f} hours")
        else:
            logger.info(f"Valid cookies found, time remaining: {time_remaining:.1f} hours")
        return True
    
    # Need to fetch new cookies
    if not automated:
        if exists and expired:
            print(f"⚠️  Existing cookies have expired")
        elif exists and force_refresh:
            print(f"🔄 Force refresh requested")
        else:
            print(f"📝 No cookies file found")
        
        print("🚀 Fetching new Pinterest cookies...")
    else:
        if exists and expired:
            logger.info("Existing cookies have expired, fetching new ones")
        else:
            logger.info("No valid cookies found, fetching new ones")
    
    # Load environment variables from .env file
    if not load_dotenv():
        error_msg = ".env file not found!"
        if not automated:
            print(f"❌ {error_msg}")
            print("Create .env file with:")
            print("ACCOUNT=your_email@example.com")
            print("password=your_password")
        else:
            logger.error(error_msg)
        return False
    
    # Get credentials from environment variables
    email = os.getenv('ACCOUNT')
    password = os.getenv('PASSWORD')
    
    if not email or not password:
        error_msg = "Email or password not found in .env file"
        if not automated:
            print(f"❌ {error_msg}")
        else:
            logger.error(error_msg)
        return False
    
    try:
        if not automated:
            print(f"🌐 Logging in to Pinterest as: {email}")
        else:
            logger.info(f"Logging in to Pinterest as: {email}")
        
        # Login using browser - use headless mode for automated tasks
        cookies = (
            PinterestDL.with_browser(
                browser_type="firefox",
                headless=automated,  # Use headless mode for automated tasks
                incognito=False,
                verbose=not automated,  # Reduce verbosity for automated tasks
            )
            .login(email, password)
            .get_cookies(after_sec=7)
        )

        # Save cookies to file in project root
        with open(cookies_path, "w") as f:
            json.dump(cookies, f, indent=4)
        
        # Check new cookie expiry
        _, _, new_time_remaining = check_cookies_expired(cookies_path)
        
        if not automated:
            print(f"✅ Login successful! New cookies saved to {cookies_path}")
            print(f"🍪 Captured {len(cookies)} cookies")
            print(f"⏰ New cookies valid for: {new_time_remaining:.1f} hours")
        else:
            logger.info(f"Login successful! Captured {len(cookies)} cookies, valid for {new_time_remaining:.1f} hours")
        
        return True
        
    except Exception as e:
        error_msg = f"Login failed: {str(e)}"
        if not automated:
            print(f"❌ {error_msg}")
            print("💡 Try using the CLI method instead")
        else:
            logger.error(error_msg)
        return False


def get_valid_pinterest_cookies(automated=True):
    """
    Get valid Pinterest cookies for API usage
    Automatically handles cookie refresh if needed
    
    Args:
        automated (bool): If True, runs in automated mode (for cron tasks)
    
    Returns:
        list: List of cookie dictionaries if successful, None if failed
    """
    cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.json")
    
    # Ensure we have valid cookies
    if not get_pinterest_cookies_python(automated=automated):
        return None
    
    try:
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
        return cookies
    except Exception as e:
        if automated:
            logger.error(f"Error loading cookies: {e}")
        else:
            print(f"❌ Error loading cookies: {e}")
        return None


def format_cookies_for_requests(cookies_list):
    """
    Convert Pinterest cookies to format suitable for requests library
    
    Args:
        cookies_list (list): List of cookie dictionaries from Pinterest
    
    Returns:
        dict: Dictionary of cookie name-value pairs for requests
    """
    if not cookies_list:
        return {}
    
    return {cookie['name']: cookie['value'] for cookie in cookies_list if 'name' in cookie and 'value' in cookie}


def download_home_feed():
    # Simple example: Download 10 images from home feed using scrape_and_download
    print("🚀 Home Feed Download Example")
    print("=" * 50)
    
    try:
        print("📱 Downloading images from your Pinterest home feed...")
        
        # Use scrape_and_download directly - this will actually download the files
        ## List[PinterestImage]
        images = (
            PinterestDL.with_browser(
                browser_type="firefox",
                timeout=10,
                headless=True,
                incognito=False,
                verbose=True,
                ensure_alt=False,
            )
            .with_cookies_path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.json"))
            .scrape(
                url="https://www.pinterest.com",
                num=10,
            )
        )

        # Save the images to a database
        image_instances = []
        for image in images:
            image_instances.append(ImageURL(
                src=image.src,
                alt=image.alt,
                origin=image.origin,
                fallback_urls=image.fallback_urls
            ))
        
        # save to database using bulk_create for better performance
        if image_instances:
            ImageURL.objects.bulk_create(image_instances, ignore_conflicts=True)
            logger.info(f"✅ Successfully saved {len(image_instances)} images to database")

    except Exception as e:
        logger.error(f"❌ Error: {e}")

  