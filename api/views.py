from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils import timezone

# Create your views here.

class HealthCheckView(APIView):
    """
    API endpoint for health check - accessible without authentication
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return API health status
        """
        data = {
            'status': 'healthy',
            'message': 'API is running successfully!',
            'timestamp': timezone.now(),
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health/',
                'admin': '/admin/',
                'auth': '/api/auth/',
                'api_root': '/api/',
            }
        }
        return Response(data, status=status.HTTP_200_OK)
