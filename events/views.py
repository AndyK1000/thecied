from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime
from .models import Event, EventRegistration, Reservation, EventClass, Venue


def is_admin(user):
    """Check if user is an admin (superuser or staff)"""
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@user_passes_test(is_admin, login_url='/admin/login/')
def event_list(request):
    """Display list of all upcoming events"""
    # Get upcoming events that are active
    events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).order_by('date')
    
    # Get search query if provided
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'events': events,
        'search_query': search_query,
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, event_id):
    """Display detailed view of a specific event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is already registered
    user_registered = False
    if request.user.is_authenticated:
        user_registered = EventRegistration.objects.filter(
            event=event,
            user=request.user
        ).exists()
    
    # Get registration count
    registration_count = event.registrations.count()
    
    context = {
        'event': event,
        'user_registered': user_registered,
        'registration_count': registration_count,
        'spots_remaining': (
            event.max_participants - registration_count
            if event.max_participants else None
        ),
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def register_for_event(request, event_id):
    """Register the current user for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user can register
    if not event.can_register:
        messages.error(request, 'Registration for this event is not available.')
        return redirect('event_detail', event_id=event.id)
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('event_detail', event_id=event.id)
    
    # Check if event is full
    if event.max_participants:
        current_registrations = event.registrations.count()
        if current_registrations >= event.max_participants:
            messages.error(request, 'This event is full.')
            return redirect('event_detail', event_id=event.id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        # Create registration
        EventRegistration.objects.create(
            event=event,
            user=request.user,
            notes=notes
        )
        
        messages.success(
            request,
            f'Successfully registered for {event.title}!'
        )
        return redirect('event_detail', event_id=event.id)
    
    context = {'event': event}
    return render(request, 'events/register.html', context)


@login_required
def unregister_from_event(request, event_id):
    """Unregister the current user from an event"""
    event = get_object_or_404(Event, id=event_id)
    
    try:
        registration = EventRegistration.objects.get(
            event=event,
            user=request.user
        )
        registration.delete()
        messages.success(
            request,
            f'Successfully unregistered from {event.title}.'
        )
    except EventRegistration.DoesNotExist:
        messages.error(request, 'You are not registered for this event.')
    
    return redirect('event_detail', event_id=event.id)


@login_required
def my_events(request):
    """Display events the user has registered for"""
    registrations = EventRegistration.objects.filter(
        user=request.user
    ).select_related('event').order_by('event__date')
    
    context = {'registrations': registrations}
    return render(request, 'events/my_events.html', context)


def reservation_list(request):
    """Display list of all approved reservations (public calendar)"""
    reservations = Reservation.objects.filter(
        status='approved',
        event_datetime_begin__gte=timezone.now()
    ).order_by('event_datetime_begin')
    
    context = {
        'reservations': reservations,
    }
    return render(request, 'events/reservation_list.html', context)


def reservation_detail(request, reservation_id):
    """Display detailed view of a specific reservation"""
    reservation = get_object_or_404(
        Reservation, 
        event_id=reservation_id,
        status='approved'
    )
    
    context = {'reservation': reservation}
    return render(request, 'events/reservation_detail.html', context)


def create_reservation(request):
    """Create a new reservation request"""
    if request.method == 'POST':
        # Get form data
        organization = request.POST.get('organization', '')
        event_type = request.POST.get('event_type', '')
        datetime_begin = request.POST.get('datetime_begin', '')
        duration_hours = request.POST.get('duration_hours', '2')
        area = request.POST.get('area', '')
        people_min = request.POST.get('people_min', '1')
        people_max = request.POST.get('people_max', '1')
        special_requests = request.POST.get('special_requests', '')
        
        try:
            # Parse datetime
            from datetime import datetime, timedelta
            dt_begin = datetime.strptime(datetime_begin, '%Y-%m-%dT%H:%M')
            dt_begin = timezone.make_aware(dt_begin)
            
            # Create duration
            duration = timedelta(hours=float(duration_hours))
            
            # Create reservation
            reservation = Reservation.objects.create(
                event_organization=organization,
                event_type=event_type,
                event_datetime_begin=dt_begin,
                event_datetime_delta=duration,
                event_area=area,
                event_number_of_people_min=int(people_min),
                event_number_of_people_max=int(people_max),
                event_specialrequests=special_requests,
            )
            
            messages.success(
                request,
                f'Reservation request submitted successfully! '
                f'Reservation ID: {reservation.event_id}. '
                f'Your request is pending review.'
            )
            return redirect('reservation_detail', reservation_id=reservation.event_id)
            
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid data provided: {str(e)}')
    
    context = {
        'areas': [
            'Main Conference Room',
            'Small Meeting Room',
            'Workshop Space',
            'Auditorium',
            'Outdoor Area',
            'Entire Facility',
        ],
        'event_types': [
            'Conference',
            'Workshop',
            'Meeting',
            'Training Session',
            'Presentation',
            'Social Event',
            'Other',
        ]
    }
    return render(request, 'events/create_reservation.html', context)


# API Views
@require_http_methods(["GET"])
def api_event_classes(request):
    """API endpoint to get all event classes for dropdown"""
    try:
        event_classes = EventClass.objects.all().values('event_model_id', 'event_name', 'description')
        return JsonResponse({
            'success': True,
            'data': list(event_classes)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_venues(request):
    """API endpoint to get all venues for dropdown"""
    try:
        venues = Venue.objects.all().values('v_id', 'venue', 'capacity', 'description')
        return JsonResponse({
            'success': True,
            'data': list(venues)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_create_event(request):
    """API endpoint to create a new event"""
    try:
        data = json.loads(request.body)
        
        # Extract and validate required fields
        title = data.get('title')
        event_type_id = data.get('eventType')  # EventClass ID
        start_date = data.get('datetimeStart')
        end_date = data.get('datetimeEnd')
        venue_id = data.get('area')  # Venue ID
        crowd_size = data.get('crowdSize')
        special_requests = data.get('specialRequests', '')
        
        if not all([title, event_type_id, start_date, venue_id]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: title, eventType, datetimeStart, area'
            }, status=400)
        
        # Parse datetime
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            start_datetime = timezone.make_aware(start_datetime) if timezone.is_naive(start_datetime) else start_datetime
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid start date format'
            }, status=400)
        
        # Get EventClass and Venue objects
        try:
            event_class = EventClass.objects.get(event_model_id=event_type_id)
        except EventClass.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid event type'
            }, status=400)
        
        try:
            venue = Venue.objects.get(v_id=venue_id)
        except Venue.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid venue'
            }, status=400)
        
        # Parse crowd size for participant bounds
        participant_lower = 1
        participant_upper = 1
        
        if crowd_size == 'intimate':
            participant_lower, participant_upper = 1, 5
        elif crowd_size == 'small':
            participant_lower, participant_upper = 6, 15
        elif crowd_size == 'medium':
            participant_lower, participant_upper = 16, 30
        elif crowd_size == 'large':
            participant_lower, participant_upper = 31, 60
        elif crowd_size == 'xlarge':
            participant_lower, participant_upper = 61, 100
        elif crowd_size == 'massive':
            participant_lower, participant_upper = 100, 500
        
        # Create event
        event = Event.objects.create(
            title=title,
            description=special_requests,
            date=start_datetime,
            venue=venue,
            event_class=event_class,
            organizer=request.user,
            number_of_participants_lowerbound=participant_lower,
            number_of_participants_upperbound=participant_upper,
            schedule_status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'event_id': event.id,
                'title': event.title,
                'date': event.date.isoformat(),
                'venue': event.venue.venue,
                'status': event.schedule_status
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
