from django.urls import path
from . import views

app_name = 'system_status'

urlpatterns = [
    path('', views.status_page, name='status_page'),
    path('api/', views.status_api, name='status_api'),
    path('api/system/', views.system_info_api, name='system_info_api'),
]
