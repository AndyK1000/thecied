from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Venue(models.Model):
    """Model for venue information with multiple photos"""
    
    v_id = models.AutoField(primary_key=True)
    venue = models.CharField(max_length=200, help_text="Name of the venue")
    address = models.TextField(help_text="Full address of the venue")
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum capacity of the venue"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the venue and its facilities"
    )
    guy_in_charge = models.ForeignKey(
        'entitypool.Individuals',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Person responsible for this venue"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number for the venue"
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for the venue"
    )
    
    # Multiple photo fields
    photo1 = models.ImageField(
        upload_to='venues/',
        blank=True,
        null=True,
        help_text="Primary photo of the venue"
    )
    photo2 = models.ImageField(
        upload_to='venues/',
        blank=True,
        null=True,
        help_text="Secondary photo of the venue"
    )
    photo3 = models.ImageField(
        upload_to='venues/',
        blank=True,
        null=True,
        help_text="Third photo of the venue"
    )
    photo4 = models.ImageField(
        upload_to='venues/',
        blank=True,
        null=True,
        help_text="Fourth photo of the venue"
    )
    photo5 = models.ImageField(
        upload_to='venues/',
        blank=True,
        null=True,
        help_text="Fifth photo of the venue"
    )
    photo6 = models.ImageField(
        upload_to='venues/',
        blank=True,
        null=True,
        help_text="Sixth photo of the venue"
    )
    
    # Additional fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['venue']
        verbose_name = "Venue"
        verbose_name_plural = "Venues"
    
    def __str__(self):
        return self.venue
    
    @property
    def photo_count(self):
        """Count how many photos are uploaded"""
        photos = [self.photo1, self.photo2, self.photo3, self.photo4, self.photo5, self.photo6]
        return sum(1 for photo in photos if photo)


class EventClass(models.Model):
    """Model for event types/models/operating models (event classification)"""
    
    event_model_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=200, help_text="Name of the event class/type")
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this event class"
    )
    photo1 = models.ImageField(
        upload_to='event_classes/',
        blank=True,
        null=True,
        help_text="Primary photo for this event class"
    )
    photo2 = models.ImageField(
        upload_to='event_classes/',
        blank=True,
        null=True,
        help_text="Secondary photo for this event class"
    )
    
    class Meta:
        verbose_name = "Event Class"
        verbose_name_plural = "Event Classes"
        ordering = ['event_name']
    
    def __str__(self):
        return self.event_name


class Event(models.Model):
    """Model for storing event information"""
    
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(blank=True, null=True, help_text="Detailed event description")
    date = models.DateTimeField(help_text="Event date and time")
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Venue where the event will be held"
    )
    event_class = models.ForeignKey(
        EventClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Classification/type of this event"
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who organized this event"
    )
    number_of_participants_lowerbound = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum expected number of participants"
    )
    number_of_participants_upperbound = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum expected number of participants"
    )
    schedule_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('canceled', 'Canceled')
        ],
        default='pending',
        help_text="Current status of the event schedule"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
        verbose_name = "Event"
        verbose_name_plural = "Events"
    
    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_upcoming(self):
        """Check if the event is in the future"""
        return self.date > timezone.now()
    
    @property
    def can_register(self):
        """Check if users can still register for this event"""
        if self.schedule_status != 'approved':
            return False
        return self.is_upcoming


class EventRegistration(models.Model):
    """Model for storing event registrations"""
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True,
        help_text="Any additional notes from the user"
    )
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['registered_at']
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"
    
    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"


class Reservation(models.Model):
    """Model for storing event reservations and bookings"""
    
    event_id = models.AutoField(primary_key=True, help_text="Unique reservation identifier")
    event_organization = models.TextField(help_text="Organization making the reservation")
    event_type = models.TextField(help_text="Type of event (e.g., conference, workshop, meeting)")
    event_datetime_begin = models.DateTimeField(help_text="Start date and time of the event")
    event_datetime_delta = models.DurationField(help_text="Duration of the event")
    event_area = models.TextField(help_text="Area or room requested for the event")
    event_number_of_people_min = models.PositiveIntegerField(
        help_text="Minimum estimated number of people"
    )
    event_number_of_people_max = models.PositiveIntegerField(
        help_text="Maximum estimated number of people"
    )
    event_specialrequests = models.TextField(
        blank=True,
        help_text="Any special requests or requirements for the event"
    )
    
    # Additional helpful fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
        help_text="Current status of the reservation"
    )
    
    class Meta:
        ordering = ['event_datetime_begin']
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
    
    def __str__(self):
        return f"{self.event_organization} - {self.event_type} ({self.event_datetime_begin.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def event_datetime_end(self):
        """Calculate the end time of the event"""
        return self.event_datetime_begin + self.event_datetime_delta
    
    @property
    def duration_hours(self):
        """Get duration in hours for easier display"""
        return self.event_datetime_delta.total_seconds() / 3600
    
    def clean(self):
        """Validate that min people <= max people"""
        if self.event_number_of_people_min > self.event_number_of_people_max:
            raise ValidationError(
                "Minimum number of people cannot be greater than maximum number of people."
            )
