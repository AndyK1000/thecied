from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Event, EventRegistration


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
