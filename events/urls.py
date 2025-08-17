from django.urls import path
from . import views

urlpatterns = [
    # Event URLs
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('<int:event_id>/unregister/', views.unregister_from_event, name='unregister_from_event'),
    path('my-events/', views.my_events, name='my_events'),
    
    # Reservation URLs
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.create_reservation, name='create_reservation'),
    path('reservations/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    
    # API URLs
    path('api/event-classes/', views.api_event_classes, name='api_event_classes'),
    path('api/venues/', views.api_venues, name='api_venues'),
    path('api/create-event/', views.api_create_event, name='api_create_event'),
]
