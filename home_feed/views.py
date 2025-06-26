from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import random
from .models import ImageURL
from .services import ImageScrapingService, ImageURLManager
from .authentication import APIKeyAuthentication

@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def home_feed(request):
    """
    Return random image URLs for the home feed
    Query params:
    - count: number of images to return (default: 1, max: 10)
    
    Authentication:
    - Requires API key in Authorization header: "Authorization: Api-Key <your_api_key>"
    """
    try:
        # Get count parameter
        count = int(request.GET.get('count', 1))
        count = min(count, 10)  # Limit to 10 images max
        
        # Get total count of available images
        total_available = ImageURLManager.get_active_count()
        
        if total_available == 0:
            return Response({
                'message': 'No images available. Please run the scraping task first.',
                'images': []
            }, status=status.HTTP_200_OK)
        
        # Get random selection using service layer
        selected_images = ImageURLManager.get_random_urls(count)
        
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
            'total_available': total_available,
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
    try:
        # Get count parameter (optional)
        count = int(request.data.get('count', 20))
        count = min(count, 50)  # Limit to 50 images max for scraping
        
        # Use the service to scrape images
        scraping_service = ImageScrapingService()
        result = scraping_service.scrape_home_images(count)
        
        if result['success']:
            return Response({
                'message': result['message'],
                'new_images_count': result['new_images_count'],
                'total_images': result['total_images']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except ValueError:
        return Response({
            'error': 'Invalid count parameter. Must be a number.'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
