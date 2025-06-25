from django.core.management.base import BaseCommand
from home_feed.services import ImageScrapingService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape images from Pinterest home feed - automated for cron tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of images to scrape (default: 20)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(f'🚀 Starting automated image scraping (target: {count} images)...')
        logger.info(f'Starting automated image scraping for {count} images')
        
        try:
            # Create scraping service instance
            scraping_service = ImageScrapingService()
            
            # Call the scraping method with specified count
            result = scraping_service.scrape_home_images(count=count)
            
            # Handle result (now expecting dictionary format)
            if result and result.get('success', False):
                new_count = result.get('new_images_count', 0)
                total_count = result.get('total_images', 0)
                message = result.get('message', 'Success')
                
                success_message = f"✅ {message} - Added {new_count} new images (Total: {total_count})"
                self.stdout.write(success_message)
                logger.info(success_message)
                
                # Exit with success code for cron monitoring
                return
                
            else:
                error_message = result.get('message', 'Scraping failed with unknown error') if result else 'Scraping returned no result'
                error_output = f"❌ Scraping failed: {error_message}"
                self.stdout.write(error_output)
                logger.error(error_output)
                
                # Exit with error code for cron monitoring
                exit(1)
                
        except Exception as e:
            error_message = f"❌ Image scraping failed with exception: {str(e)}"
            self.stdout.write(error_message)
            logger.error(error_message, exc_info=True)
            
            # Exit with error code for cron monitoring
            exit(1)
        
        logger.info('Image scraping completed') 
