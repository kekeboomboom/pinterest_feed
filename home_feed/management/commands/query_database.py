from django.core.management.base import BaseCommand
from home_feed.models import ImageURL


class Command(BaseCommand):
    help = 'Query the actual database (not test database) to see saved images'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Querying actual development database'))
        self.stdout.write('=' * 50)
        
        # Get total count
        total_count = ImageURL.objects.count()
        self.stdout.write(f"Total images in database: {total_count}")
        
        # Get one record
        if total_count > 0:
            image = ImageURL.objects.first()
            self.stdout.write(f"\nFirst image record:")
            self.stdout.write(f"  ID: {image.id}")
            self.stdout.write(f"  Alt: {image.alt}")
            self.stdout.write(f"  Source: {image.src}")
            self.stdout.write(f"  Active: {image.is_active}")
            
            self.stdout.write(self.style.SUCCESS("✅ Query successful"))
        else:
            self.stdout.write("No images found in database")
            self.stdout.write("💡 Run 'python3 manage.py test_download_feed' first to add data") 
