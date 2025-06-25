from django.test import TestCase
from .models import ImageURL


class ImageURLQueryTest(TestCase):
    """Simple test to query one ImageURL record from database"""
    
    def test_query_one_record(self):
        """Query one record from existing database"""
        print("\n🔍 Testing simple database query")
        
        # Create a sample record for testing
        test_image = ImageURL.objects.create(
            src="https://example.com/test.jpg",
            alt="Test image for unit test",
            origin="https://example.com",
            fallback_urls=["https://example.com/fallback.jpg"]
        )
        
        # Get total count
        total_count = ImageURL.objects.count()
        print(f"Total images in database: {total_count}")
        
        # Get one record
        if total_count > 0:
            image = ImageURL.objects.first()
            print(f"\nFirst image record:")
            print(f"  ID: {image.id}")  # type: ignore
            print(f"  Alt: {image.alt}")  # type: ignore
            print(f"  Source: {image.src}")  # type: ignore
            print(f"  Active: {image.is_active}")  # type: ignore
            
            # Simple assertion
            self.assertIsNotNone(image)
            self.assertEqual(image.alt, "Test image for unit test")  # type: ignore
            print("✅ Query successful")
        else:
            print("No images found in database")
            print("💡 This shouldn't happen as we created a test record")
