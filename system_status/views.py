from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
import platform
import psutil
import os
import time
from datetime import datetime
from events.models import Venue
from manage_suites.models import SuiteContracts

def is_admin(user):
    return user.is_authenticated and user.is_staff

def status_page(request):
    """Serve the system status page"""
    return render(request, 'status.html')

def system_info_api(request):
    """Get system information API endpoint"""
    try:
        # Get system information
        system_info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'uptime': get_uptime(),
            'memory': get_memory_info(),
            'disk': get_disk_info(),
            'cpu': get_cpu_info(),
            'timestamp': datetime.now().isoformat()
        }
        
        return JsonResponse(system_info)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_uptime():
    """Get system uptime"""
    try:
        if platform.system() == "Windows":
            import uptime
            return str(uptime.uptime())
        else:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_string = str(datetime.fromtimestamp(uptime_seconds))
                return uptime_string
    except:
        return "N/A"

def get_memory_info():
    """Get memory usage information"""
    try:
        memory = psutil.virtual_memory()
        return {
            'total': f"{memory.total / (1024**3):.2f} GB",
            'used': f"{memory.used / (1024**3):.2f} GB",
            'available': f"{memory.available / (1024**3):.2f} GB",
            'percent': f"{memory.percent}%"
        }
    except:
        return "N/A"

def get_disk_info():
    """Get disk usage information"""
    try:
        disk = psutil.disk_usage('/')
        return {
            'total': f"{disk.total / (1024**3):.2f} GB",
            'used': f"{disk.used / (1024**3):.2f} GB",
            'free': f"{disk.free / (1024**3):.2f} GB",
            'percent': f"{(disk.used / disk.total) * 100:.1f}%"
        }
    except:
        return "N/A"

# Add comprehensive status API for the dashboard
def status_api(request):
    """Get comprehensive system status for dashboard"""
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/' if os.name != 'nt' else 'C:\\')
        
        # Calculate uptime in seconds
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)
        
        # Get database stats
        database_stats = get_database_stats()
        
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'sessions': {
                    'active': 1,  # Simplified for now
                    'connections': len(psutil.net_connections())
                },
                'activity': {
                    'uptime_seconds': uptime_seconds,
                    'total_requests': 0,  # Would need to track this
                    'recent_reservations': 0  # Would need to implement
                }
            },
            'database': database_stats
        }
        
        return JsonResponse(status_data)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'cpu_percent': 0,
                'memory': {'total': 0, 'available': 0, 'percent': 0, 'used': 0},
                'disk': {'total': 0, 'free': 0, 'percent': 0},
                'sessions': {'active': 0, 'connections': 0},
                'activity': {'uptime_seconds': 0, 'total_requests': 0, 'recent_reservations': 0}
            },
            'database': {'responsive': False, 'total_reservations': 0, 'total_venues': 0, 'total_suite_contracts': 0, 'total_users': 0}
        }, status=500)

def get_database_stats():
    """Get database statistics"""
    try:
        from django.db import connection
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            
        # Get counts from various models
        total_venues = Venue.objects.count()
        total_suite_contracts = SuiteContracts.objects.count()
        total_users = User.objects.count()
        
        # Get reservations count
        total_reservations = 0
        try:
            from events.models import Reservation
            total_reservations = Reservation.objects.count()
        except ImportError:
            pass
        
        return {
            'responsive': True,
            'total_reservations': total_reservations,
            'total_venues': total_venues,
            'total_suite_contracts': total_suite_contracts,
            'total_users': total_users,
            'table_count': get_table_count()
        }
    except Exception as e:
        return {
            'responsive': False,
            'error': str(e),
            'total_reservations': 0,
            'total_venues': 0,
            'total_suite_contracts': 0,
            'total_users': 0,
            'table_count': 0
        }

def get_table_count():
    """Get total number of database tables"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()"
                if connection.vendor == 'mysql' else
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                if connection.vendor == 'sqlite' else
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
            )
            return cursor.fetchone()[0]
    except:
        return 0

def get_cpu_info():
    """Get CPU usage information"""
    try:
        return {
            'usage_percent': f"{psutil.cpu_percent(interval=1)}%",
            'count': psutil.cpu_count(),
            'load_avg': getattr(os, 'getloadavg', lambda: [0, 0, 0])()
        }
    except:
        return "N/A"
