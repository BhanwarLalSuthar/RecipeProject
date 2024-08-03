import jwt
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from .models import UserProfile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class JWTAuthmiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = [
            reverse('login'),
            reverse('register'),
            reverse('resetpassword'),
            reverse('password_reset_confirm'),
            reverse('recipe_list'),
            reverse('review_list'),
            reverse('collection_list'),
            reverse('article_list'),
            reverse('product_list'),
            reverse('order_list'),
            reverse('swagger'),
            reverse('redoc'),
            '/favicon.ico',
        ]
    
    def __call__(self, request):
        if any(request.path.startswith(path) for path in self.excluded_paths) or request.path.startswith("/admin/"):
            return self.get_response(request)
        
        token = request.COOKIES.get('jwt')
        if not token:
            return JsonResponse({'message': "Unauthorized: No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            payload = jwt.decode(token, 'bhawar', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'message': "Unauthorized: Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return JsonResponse({'message': "Unauthorized: Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        profile = UserProfile.objects.filter(user_id=payload['id']).first()
        # print(profile)
        if not profile or profile.user_type != 'author':
            return JsonResponse({'message': "Unauthorized: Invalid user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        request.author = profile
        return self.get_response(request)
