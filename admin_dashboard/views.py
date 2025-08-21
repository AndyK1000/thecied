from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from datetime import datetime, timedelta
import json

from events.models import EventClass, Venue, Reservation
from entitypool.models import Individuals, Organizations
from manage_suites.models import Suites, SuiteContracts


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff


def admin_login_view(request):
    """Admin login view"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient privileges')
    
    return render(request, 'admin/login.html')


@login_required
@user_passes_test(is_admin)
def admin_logout_view(request):
    """Admin logout view"""
    logout(request)
    return redirect('admin_login')


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Serve the admin dashboard React app"""
    return render(request, 'admin/dashboard.html')


def dashboard_view(request):
    """Public dashboard view - redirects to admin dashboard if authenticated"""
    if request.user.is_authenticated and request.user.is_staff:
        return admin_dashboard_view(request)
    else:
        # Serve a public dashboard or redirect to login
        return render(request, 'dashboard.html')


# API Endpoints for Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_stats_api(request):
    """Get dashboard statistics"""
    try:
        # Calculate date ranges
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        stats = {
            'events': {
                'total': EventClass.objects.count(),
                'active': EventClass.objects.filter(is_active=True).count()
            },
            'reservations': {
                'total': Reservation.objects.count(),
                'pending': Reservation.objects.filter(status='pending').count(),
                'confirmed': Reservation.objects.filter(status='confirmed').count(),
                'cancelled': Reservation.objects.filter(status='cancelled').count(),
                'recent': Reservation.objects.filter(created_at__gte=week_ago).count()
            },
            'venues': {
                'total': Venue.objects.count(),
                'with_reservations': Venue.objects.annotate(
                    reservation_count=Count('reservation')
                ).filter(reservation_count__gt=0).count()
            },
            'suites': {
                'total': Suites.objects.count(),
                'available': Suites.objects.filter(is_available=True).count() if hasattr(Suites, 'is_available') else 0,
                'contracts': SuiteContracts.objects.count()
            },
            'entities': {
                'individuals': Individuals.objects.count(),
                'organizations': Organizations.objects.count()
            }
        }
        
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def admin_reservations_api(request):
    """Get reservations data for admin"""
    try:
        reservations = []
        for reservation in Reservation.objects.select_related('venue').order_by('-created_at')[:20]:
            reservations.append({
                'id': reservation.event_id,
                'event_organization': reservation.event_organization,
                'event_type': reservation.event_type,
                'venue': reservation.venue.venue if reservation.venue else 'N/A',
                'start_datetime': reservation.start_datetime.isoformat() if reservation.start_datetime else None,
                'duration_hours': reservation.duration_hours,
                'status': reservation.status,
                'created_at': reservation.created_at.isoformat(),
                'min_crowd_size': reservation.min_crowd_size,
                'max_crowd_size': reservation.max_crowd_size
            })
        
        return JsonResponse({'reservations': reservations})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def admin_venues_api(request):
    """Get venues data for admin"""
    try:
        venues = []
        for venue in Venue.objects.annotate(reservation_count=Count('reservation')):
            venues.append({
                'id': venue.id,
                'venue': venue.venue,
                'address': venue.address,
                'capacity': venue.capacity,
                'reservation_count': venue.reservation_count,
                'contact_email': venue.contact_email,
                'guy_in_charge': venue.guy_in_charge.full_name if venue.guy_in_charge else 'N/A'
            })
        
        return JsonResponse({'venues': venues})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def admin_suites_api(request):
    """Get suites data for admin"""
    try:
        suites = []
        for suite in Suites.objects.all():
            contracts_count = SuiteContracts.objects.filter(suite=suite).count()
            suites.append({
                'id': suite.suite_id,
                'suite_name': suite.suite_name,
                'square_footage': suite.square_footage,
                'monthly_rent': float(suite.monthly_rent),
                'contracts_count': contracts_count,
                'has_private_office': getattr(suite, 'has_private_office', False),
                'has_conference_room': getattr(suite, 'has_conference_room', False),
                'desk_count': getattr(suite, 'desk_count', 0)
            })
        
        return JsonResponse({'suites': suites})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def admin_entities_api(request):
    """Get entities (individuals and organizations) data for admin"""
    try:
        individuals = []
        for individual in Individuals.objects.all()[:10]:  # Limit to recent 10
            individuals.append({
                'id': individual.id,
                'full_name': individual.full_name,
                'email': individual.email,
                'phone': individual.phone,
                'organization': individual.organization
            })
        
        organizations = []
        for org in Organizations.objects.all()[:10]:  # Limit to recent 10
            organizations.append({
                'id': org.id,
                'organization_name': org.organization_name,
                'contact_person': org.contact_person,
                'email': org.email,
                'phone': org.phone
            })
        
        return JsonResponse({
            'individuals': individuals,
            'organizations': organizations
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
def admin_update_reservation_status(request):
    """Update reservation status"""
    try:
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        new_status = data.get('status')
        
        if not reservation_id or not new_status:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        reservation = Reservation.objects.get(event_id=reservation_id)
        reservation.status = new_status
        reservation.save()
        
        return JsonResponse({'success': True, 'message': 'Status updated successfully'})
    except Reservation.DoesNotExist:
        return JsonResponse({'error': 'Reservation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
