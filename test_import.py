import sys
import os
sys.path.insert(0, '/home/bitnami/thecied')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thecied.settings')
import django
django.setup()
print("Django settings imported successfully!")
