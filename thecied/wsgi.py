"""
WSGI config for thecied project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, '/home/bitnami/thecied')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thecied.settings')

application = get_wsgi_application()
