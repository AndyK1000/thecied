"""
URL configuration for thecied project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

def react_app(request):
    """Serve the React application"""
    # Check if this is admin subdomain
    host = request.get_host()
    if host.startswith('admin.'):
        return redirect('/admin_dashboard/')
    return render(request, 'index.html')

def reserve_page(request):
    """Serve the reserve page"""
    return render(request, 'reserve/index.html')

def legacy_home(request):
    """Legacy home page for reference"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>The CIED - Welcome</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .success { background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .info { background: #d1ecf1; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .footer { text-align: center; margin-top: 40px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Welcome to The CIED!</h1>
            <div class="success">
                <h3>✅ Deployment Successful!</h3>
                <p>Your Django application is now live on AWS Lightsail with HTTPS!</p>
            </div>
            <div class="info">
                <h3>🚀 What's Working:</h3>
                <ul>
                    <li>✅ Django 5.2.4 running on Python 3.12</li>
                    <li>✅ Django Events System</li>
                    <li>✅ Apache web server with mod_wsgi</li>
                    <li>✅ SSL/HTTPS with Let's Encrypt</li>
                    <li>✅ Domain: thecied.dev</li>
                    <li>✅ Automatic deployment pipeline</li>
                </ul>
            </div>
            <div class="info">
                <h3>🔗 Available Pages:</h3>
                <ul>
                    <li><a href="/events/" target="_blank">Events</a> - View upcoming events</li>
                    <li><a href="/admin/" target="_blank">Admin Panel</a> - Django admin</li>
                </ul>
            </div>
            <div class="footer">
                <p>🔧 Built with Django • 🚀 Deployed on AWS Lightsail • 🔒 Secured with Let's Encrypt</p>
            </div>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    path('', react_app, name='home'),
    path('reserve/', reserve_page, name='reserve'),
    path('legacy/', legacy_home, name='legacy_home'),  # Keep old home for reference
    path('admin/', admin.site.urls),
    path('admin_dashboard/', include('admin_dashboard.urls')),
    path('events/', include('events.urls')),
    # Serve images at /images/ for React app compatibility
    path('images/<path:path>', serve, {
        'document_root': os.path.join(settings.STATIC_ROOT, 'images')
    }),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
