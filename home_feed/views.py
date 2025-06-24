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
