# Pinterest Feed API - Project Initialization Guide

## Project Overview
This guide will help you set up a Django REST API for a home feed that returns image URLs, with automated daily image scraping functionality.

## Final Project Structure
```
pinterest_feed/
├── manage.py
├── requirements.txt                 # Python dependencies
├── init_project.md                 # This file
├── pinterest_feed/                 # Main Django project
│   ├── __init__.py
│   ├── settings.py                 # Updated with new apps and settings
│   ├── urls.py                     # Updated with home_feed URLs
│   ├── wsgi.py
│   └── asgi.py
├── home_feed/                      # Main app (to be created)
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── views.py                    # API endpoints
│   ├── services.py                 # Business logic (TODO)
│   ├── urls.py                     # URL routing
│   ├── utils.py                    # Helper functions (TODO)
│   ├── tests.py
│   └── management/                 # Django management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── scrape_images.py    # Cron task command (TODO)
└── db.sqlite3                     # SQLite database (auto-created)
```

## Dependencies
The `requirements.txt` file includes:
- **Django**: Web framework
- **djangorestframework**: REST API functionality
- **django-crontab**: Cron job management

## Step-by-Step Initialization

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Create Django App
```bash
python3 manage.py startapp home_feed
```

### 3. Create Required Directories
```bash
mkdir -p home_feed/management/commands
```

### 4. Update Django Settings
Edit `pinterest_feed/settings.py` and add:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',      # Add this
    'django_crontab',      # Add this
    'home_feed',           # Add this
]

# Add REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# Add Cron jobs configuration
CRONJOBS = [
    ('0 6 * * *', 'home_feed.management.commands.scrape_images.Command.handle'),
]

# SQLite database is already configured in DATABASES setting above
```

### 5. Update Main URLs
Edit `pinterest_feed/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('', include('home_feed.urls')),
]
```

### 6. Create App Files

#### Create `home_feed/models.py`
```python
from django.db import models

class ImageURL(models.Model):
    src = models.URLField(unique=True, max_length=500)
    alt = models.CharField(max_length=255, blank=True)
    origin = models.URLField(max_length=500)
    fallback_urls = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.alt}: {self.src[:50]}..."
    
    class Meta:
        ordering = ['-id']
        verbose_name = "Image URL"
        verbose_name_plural = "Image URLs"
```

#### Create `home_feed/urls.py`
```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/home_feed/', views.home_feed, name='home_feed'),
    path('api/trigger_scraping/', views.trigger_scraping, name='trigger_scraping'),
]
```

#### Create `home_feed/views.py`
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import random
from .models import ImageURL
from .services import ImageScrapingService

@api_view(['GET'])
@permission_classes([AllowAny])
def home_feed(request):
    """
    Return random image URLs for the home feed
    Query params:
    - count: number of images to return (default: 10, max: 50)
    """
    try:
        # Get count parameter
        count = int(request.GET.get('count', 10))
        count = min(count, 50)  # Limit to 50 images max
        
        # Get active URLs from database
        active_images = ImageURL.objects.filter(is_active=True)
        
        if not active_images.exists():
            return Response({
                'message': 'No images available. Please run the scraping task first.',
                'images': []
            }, status=status.HTTP_200_OK)
        
        # Get random selection
        if active_images.count() <= count:
            selected_images = active_images
        else:
            selected_images = active_images.order_by('?')[:count]  # Random order
        
        selected_images_data = [
            {
                'src': img.src,
                'alt': img.alt,
                'origin': img.origin,
                'fallback_urls': img.fallback_urls
            }
            for img in selected_images
        ]
        
        return Response({
            'message': 'Images retrieved successfully',
            'total_available': active_images.count(),
            'count': len(selected_images_data),
            'images': selected_images_data
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response({
            'error': 'Invalid count parameter. Must be a number.'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_scraping(request):
    """Manual trigger for scraping (for testing)"""
    # TODO: Implement manual scraping trigger
    pass
```

#### Create `home_feed/utils.py`
```python
import re
from urllib.parse import urlparse
from typing import List, Dict, Optional

def validate_image_url(url: str) -> bool:
    """Validate if a URL is properly formatted and potentially an image URL"""
    # TODO: Implement URL validation logic
    pass

def clean_alt_text(alt_text: str) -> str:
    """Clean and normalize alt text for images"""
    # TODO: Implement alt text cleaning
    pass

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    # TODO: Implement domain extraction
    pass

def generate_fallback_urls(original_url: str) -> List[str]:
    """Generate potential fallback URLs for an image"""
    # TODO: Implement fallback URL generation for different image sizes
    pass

def format_api_response(success: bool, message: str, data: Dict = None, error: str = None) -> Dict:
    """Standardize API response format"""
    # TODO: Implement standardized API response formatting
    pass
```

#### Create `home_feed/services.py`
```python
import requests
import random
import logging
from django.db import IntegrityError
from datetime import datetime, timedelta
from .models import ImageURL

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
    
    def scrape_all_sources(self):
        """Scrape from all available sources"""
        # TODO: Implement scraping from multiple sources
        pass
    
```

#### Create Management Command Files

Create `home_feed/management/__init__.py` (empty file)

Create `home_feed/management/commands/__init__.py` (empty file)

Create `home_feed/management/commands/scrape_images.py`:
```python
from django.core.management.base import BaseCommand
from home_feed.services import ImageScrapingService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape images from various sources for the home feed'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sources',
            type=str,
            default='all',
            help='Sources to scrape from (default: all)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting image scraping...'))
        
        # TODO: Implement scraping command logic
        pass
```

## Running the Application

### 1. Create and Apply Migrations
```bash
python3 manage.py makemigrations home_feed
python3 manage.py migrate
```

### 2. Test Manual Scraping Command
```bash
python3 manage.py scrape_images
```

### 3. Setup Cron Jobs (for production)
```bash
python3 manage.py crontab add
```

### 4. Start Development Server
```bash
python3 manage.py runserver
```

## API Endpoints

Once running, your API will be available at:

### 1. Get Home Feed Images
```
GET http://localhost:8000/api/home_feed/
GET http://localhost:8000/api/home_feed/?count=20
```

**Response Format:**
```json
{
    "message": "Images retrieved successfully",
    "total_available": 45,
    "count": 10,
    "images": [
        {
            "src": "https://i.pinimg.com/originals/48/69/a4/4869a4ba49c2fde6cb47075ad9f10c1e.jpg",
            "alt": "This may contain: an orange and white cat laying on its back",
            "origin": "https://www.pinterest.com/pin/25332816647396661/",
            "fallback_urls": [
                "https://i.pinimg.com/736x/48/69/a4/4869a4ba49c2fde6cb47075ad9f10c1e.jpg"
            ]
        }
    ]
}
```

### 2. Manual Scraping Trigger (for testing)
```
POST http://localhost:8000/api/trigger_scraping/
```

## TODO Implementation Guide

### 1. `services.py` - ImageURLManager class (Database Operations)
- Implement `add_urls()`: Insert URLs into database with duplicate handling using try/except IntegrityError
- Implement `get_random_urls()`: Query database for random active URLs using `order_by('?')`
- Implement `deactivate_old_urls()`: Update old records to set `is_active=False`

### 2. `services.py` - ImageScrapingService class (Business Logic)
- Implement `scrape_picsum_images()`:
  - Generate Lorem Picsum URLs with random dimensions
  - Return list of placeholder image URLs
- Implement `scrape_all_sources()`:
  - Call scraping methods (start with picsum for simplicity)
  - Use `ImageURLManager.add_urls()` to save to database
  - Return count of new images added

### 3. `utils.py` - General Utility Functions
- Implement `validate_image_url()`: Check if URL is properly formatted and potentially an image
- Implement `clean_alt_text()`: Remove common prefixes and normalize alt text
- Implement `extract_domain()`: Extract domain from URL for categorization
- Implement `generate_fallback_urls()`: Create fallback URLs for different image sizes
- Implement `format_api_response()`: Standardize API response format

### 4. `views.py` - trigger_scraping view
- Instantiate ImageScrapingService
- Call scrape_all_sources()
- Return JSON response with success/error status

### 5. `scrape_images.py` - Management command
- Implement `handle()` method
- Call ImageScrapingService.scrape_all_sources()
- Add proper logging and error handling

## Testing

### Manual Testing
1. Start the server: `python3 manage.py runserver`
2. Test scraping: `POST http://localhost:8000/api/trigger_scraping/`
3. Test feed: `GET http://localhost:8000/api/home_feed/`

### Command Line Testing
```bash
# Test the management command
python3 manage.py scrape_images

# Check database entries
python3 manage.py shell
# In Django shell:
# >>> from home_feed.models import ImageURL
# >>> ImageURL.objects.count()
# >>> ImageURL.objects.all()[:5]
```

## Production Considerations

1. **Environment Variables**: Move sensitive settings to environment variables
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Error Handling**: Implement comprehensive error logging
4. **Monitoring**: Add health check endpoints
5. **Caching**: Consider Redis for better performance
6. **Image Validation**: Validate that URLs return actual images

## Architecture Benefits

- **Separation of Concerns**: Views handle HTTP, Services handle business logic
- **No Database Required**: Uses simple file storage for URLs
- **Modular Design**: Easy to add new image sources
- **Testable**: Each component can be tested independently
- **Configurable**: Easy to adjust scraping frequency and sources 
