from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Event(models.Model):
    """Model for storing event information"""
    
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(help_text="Detailed event description")
    date = models.DateTimeField(help_text="Event date and time")
    location = models.CharField(max_length=300, help_text="Event location")
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who organized this event"
    )
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants (leave blank for unlimited)"
    )
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last date for registration (leave blank if no deadline)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the event is active and accepting registrations"
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
        if not self.is_active:
            return False
        if self.registration_deadline and self.registration_deadline < timezone.now():
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
