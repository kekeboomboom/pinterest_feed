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
        # TODO: Implement database insertion with duplicate handling
        pass
    
    @staticmethod
    def get_random_urls(count=10):
        """Get random active URLs from database"""
        # TODO: Implement random URL retrieval
        pass
    
    @staticmethod
    def deactivate_old_urls(days=30):
        """Deactivate URLs older than specified days"""
        # TODO: Implement URL cleanup logic
        pass

class ImageScrapingService:
    def __init__(self):
        self.url_manager = ImageURLManager()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_home_images(self, count=20):
        """Scrape images from Unsplash (free high-quality images)"""
        # TODO: Implement Unsplash scraping logic

        pass
    


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


def get_pinterest_cookies_python(force_refresh=False):
    """
    Smart Pinterest cookie management
    Checks for existing cookies and their expiry before fetching new ones
    
    Args:
        force_refresh (bool): If True, forces new cookie fetch regardless of expiry
    
    Returns:
        bool: True if cookies are available and valid, False otherwise
    """
    print("\n🔑 Smart Pinterest Cookie Manager")
    print("=" * 50)
    
    # Get cookies file path
    cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.json")
    
    # Check existing cookies first
    exists, expired, time_remaining = check_cookies_expired(cookies_path)
    
    if exists and not expired and not force_refresh:
        print(f"✅ Valid cookies found!")
        print(f"📁 Cookie file: {cookies_path}")
        print(f"⏰ Time remaining: {time_remaining:.1f} hours")
        return True
    
    # Need to fetch new cookies
    if exists and expired:
        print(f"⚠️  Existing cookies have expired")
    elif exists and force_refresh:
        print(f"🔄 Force refresh requested")
    else:
        print(f"📝 No cookies file found")
    
    print("🚀 Fetching new Pinterest cookies...")
    
    # Load environment variables from .env file
    if not load_dotenv():
        print("❌ .env file not found!")
        print("Create .env file with:")
        print("account=your_email@example.com")
        print("password=your_password")
        return False
    
    # Get credentials from environment variables
    email = os.getenv('account')
    password = os.getenv('password')
    
    if not email or not password:
        print("❌ Email or password not found in .env file")
        return False
    
    try:
        print(f"🌐 Logging in to Pinterest as: {email}")
        
        # Login using browser
        cookies = (
            PinterestDL.with_browser(
                browser_type="firefox",
                headless=False,
                incognito=False,
                verbose=False,
            )
            .login(email, password)
            .get_cookies(after_sec=7)
        )

        # Save cookies to file in project root
        with open(cookies_path, "w") as f:
            json.dump(cookies, f, indent=4)
        
        # Check new cookie expiry
        _, _, new_time_remaining = check_cookies_expired(cookies_path)
        
        print(f"✅ Login successful! New cookies saved to {cookies_path}")
        print(f"🍪 Captured {len(cookies)} cookies")
        print(f"⏰ New cookies valid for: {new_time_remaining:.1f} hours")
        
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        print("💡 Try using the CLI method instead")
        return False


def get_valid_pinterest_cookies():
    """
    Get valid Pinterest cookies for API usage
    Automatically handles cookie refresh if needed
    
    Returns:
        list: List of cookie dictionaries if successful, None if failed
    """
    cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.json")
    
    # Ensure we have valid cookies
    if not get_pinterest_cookies_python():
        return None
    
    try:
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
        return cookies
    except Exception as e:
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
