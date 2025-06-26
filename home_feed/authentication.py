from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    """
    Simple API key based authentication.
    
    Clients should authenticate by passing the API key in the request header.
    For example:
        Authorization: Api-Key 401f7ac837da42b97f613d789819ff93537bee6a
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None

        try:
            auth_type, api_key = auth_header.split(' ', 1)
        except ValueError:
            raise AuthenticationFailed('Invalid authorization header format')

        if auth_type.lower() != 'api-key':
            return None

        return self.authenticate_credentials(api_key)

    def authenticate_credentials(self, key):
        try:
            api_key = APIKey.objects.get(key=key, is_active=True)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

        # Update last used timestamp
        api_key.last_used = timezone.now()
        api_key.save(update_fields=['last_used'])

        # Return a dummy user (None) and the API key
        return (None, api_key)

    def authenticate_header(self, request):
        return 'Api-Key'