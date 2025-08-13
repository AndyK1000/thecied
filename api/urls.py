from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
# router.register(r'users', views.UserViewSet)  # Example - we'll add this later

# API URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.HealthCheckView.as_view(), name='api-health'),
    path('auth/', include('rest_framework.urls')),  # DRF login/logout views
]
