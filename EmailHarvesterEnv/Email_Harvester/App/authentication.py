from rest_framework import authentication
from rest_framework import exceptions
from .models import APIKey

class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        try:
            api_key_obj = APIKey.objects.get(key=api_key)
            return (api_key_obj.user, None)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key')