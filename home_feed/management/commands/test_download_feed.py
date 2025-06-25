from django.core.management.base import BaseCommand
from django.db import connection
from home_feed.services import download_home_feed
from home_feed.models import ImageURL


class Command(BaseCommand):
    help = 'Test the download_home_feed method and database operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-db',
            action='store_true',
            help='Clear existing images from database before testing',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of random images to display from database (default: 5)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Testing Pinterest Home Feed Download'))
        self.stdout.write('=' * 60)

        # Clear database if requested
        if options['clear_db']:
            self.stdout.write('\n🗑️  Clearing existing images from database...')
            deleted_count = ImageURL.objects.count()
            ImageURL.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'   Deleted {deleted_count} existing images'))

        # Show initial database state
        self.stdout.write('\n📊 Initial Database State:')
        initial_count = ImageURL.objects.count()
        self.stdout.write(f'   Total images in database: {initial_count}')

        # Test the download_home_feed method
        self.stdout.write('\n🔽 Testing download_home_feed method...')
        try:
            download_home_feed()
            self.stdout.write(self.style.SUCCESS('   ✅ download_home_feed completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error in download_home_feed: {str(e)}'))
            return

        # Show updated database state
        self.stdout.write('\n📊 Updated Database State:')
        final_count = ImageURL.objects.count()
        new_images = final_count - initial_count
        self.stdout.write(f'   Total images in database: {final_count}')
        self.stdout.write(f'   New images added: {new_images}')

        # Display some sample images from database
        self.stdout.write(f'\n🖼️  Sample Images from Database (showing {options["count"]} random images):')
        sample_images = ImageURL.objects.order_by('?')[:options['count']]
        
        if sample_images:
            for i, image in enumerate(sample_images, 1):
                self.stdout.write(f'\n   {i}. ID: {image.id}')
                self.stdout.write(f'      Alt: {image.alt}')
                self.stdout.write(f'      Source: {image.src}')
                self.stdout.write(f'      Origin: {image.origin}')
                self.stdout.write(f'      Fallback URLs: {len(image.fallback_urls)} URLs')
                self.stdout.write(f'      Active: {image.is_active}')
        else:
            self.stdout.write('   No images found in database')

        # Database statistics
        self.stdout.write('\n📈 Database Statistics:')
        active_count = ImageURL.objects.filter(is_active=True).count()
        inactive_count = ImageURL.objects.filter(is_active=False).count()
        self.stdout.write(f'   Active images: {active_count}')
        self.stdout.write(f'   Inactive images: {inactive_count}')

        # Test database queries
        self.stdout.write('\n🔍 Testing Database Queries:')
        
        # Test getting images with alt text
        with_alt = ImageURL.objects.exclude(alt='').count()
        self.stdout.write(f'   Images with alt text: {with_alt}')
        
        # Test getting images with fallback URLs
        with_fallbacks = ImageURL.objects.exclude(fallback_urls=[]).count()
        self.stdout.write(f'   Images with fallback URLs: {with_fallbacks}')

        # Show recent images
        recent_images = ImageURL.objects.order_by('-id')[:3]
        self.stdout.write('\n🕒 Most Recent Images:')
        for image in recent_images:
            self.stdout.write(f'   • {image.alt or "No alt text"} - {image.src[:50]}...')

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Test completed successfully!')) 
