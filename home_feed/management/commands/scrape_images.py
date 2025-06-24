from django.core.management.base import BaseCommand
from home_feed.services import ImageScrapingService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape images from various sources for the home feed'
    
    def handle(self, *args, **options):
        logger.info('Starting image scraping...')
        
        try:
            # Create scraping service instance
            scraping_service = ImageScrapingService()
            
            # Call the scraping method
            result = scraping_service.scrape_home_images()
            
            # Handle successful result
            if result and result.get('success', False):
                new_count = result.get('new_images_count', 0)
                total_count = result.get('total_images', 0)
                
                success_message = f"Successfully added {new_count} new images to database (Total: {total_count})"
                logger.info(success_message)
            else:
                error_message = result.get('message', 'Scraping failed with unknown error') if result else 'Scraping returned no result'
                logger.error(f"Scraping failed: {error_message}")
                
        except Exception as e:
            error_message = f"Image scraping failed with exception: {str(e)}"
            logger.error(error_message, exc_info=True)
        
        logger.info('Image scraping completed') 
