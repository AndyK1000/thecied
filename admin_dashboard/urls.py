from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    
    # API endpoints
    path('api/stats/', views.admin_stats_api, name='admin_stats_api'),
    path('api/reservations/', views.admin_reservations_api, name='admin_reservations_api'),
    path('api/venues/', views.admin_venues_api, name='admin_venues_api'),
    path('api/suites/', views.admin_suites_api, name='admin_suites_api'),
    path('api/entities/', views.admin_entities_api, name='admin_entities_api'),
    path('api/reservation/status/', views.admin_update_reservation_status, name='admin_update_reservation_status'),
]
