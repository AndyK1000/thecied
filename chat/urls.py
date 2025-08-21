from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_page, name='chat_page'),
    path('api/', views.chat_api, name='chat_api'),
    path('history/', views.get_chat_history, name='chat_history'),
]
