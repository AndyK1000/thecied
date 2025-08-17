from django.contrib import admin
from .models import Event, EventRegistration, Reservation, EventClass, Venue


@admin.register(EventClass)
class EventClassAdmin(admin.ModelAdmin):
    list_display = ['event_model_id', 'event_name', 'description', 'has_photo1', 'has_photo2']
    search_fields = ['event_name', 'description']
    ordering = ['event_name']
    
    fieldsets = (
        ('Event Class Information', {
            'fields': ('event_name', 'description')
        }),
        ('Photos', {
            'fields': ('photo1', 'photo2'),
            'classes': ('drag-drop-upload',),
            'description': 'Upload photos by dragging and dropping files or clicking to browse.'
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/drag_drop_upload.css',)
        }
        js = ('admin/js/drag_drop_upload.js',)
    
    def has_photo1(self, obj):
        """Show if photo1 is uploaded"""
        return bool(obj.photo1)
    has_photo1.boolean = True
    has_photo1.short_description = 'Photo 1'
    
    def has_photo2(self, obj):
        """Show if photo2 is uploaded"""
        return bool(obj.photo2)
    has_photo2.boolean = True
    has_photo2.short_description = 'Photo 2'


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = [
        'v_id', 'venue', 'capacity', 
        'photo_count_display', 'contact_phone', 'created_at'
    ]
    list_filter = ['capacity', 'created_at']
    search_fields = ['venue', 'address', 'description', 'contact_phone', 'contact_email']
    date_hierarchy = 'created_at'
    readonly_fields = ['v_id', 'created_at', 'updated_at', 'photo_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('venue', 'address', 'description', 'capacity')
        }),
        ('Supervisor', {
            'fields': ('guy_in_charge', 'contact_phone', 'contact_email'),
            'description': 'Person responsible for this venue and contact information.'
        }),
        ('Photos', {
            'fields': ('photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photo6'),
            'classes': ('drag-drop-upload',),
            'description': 'Upload venue photos by dragging and dropping files or clicking to browse. You can upload up to 6 photos.'
        }),
        ('System Information', {
            'fields': ('v_id', 'photo_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    class Media:
        css = {
            'all': ('admin/css/drag_drop_upload.css',)
        }
        js = ('admin/js/drag_drop_upload.js',)
    
    def photo_count_display(self, obj):
        """Display photo count in list view"""
        count = obj.photo_count
        return f"{count}/6 photos"
    photo_count_display.short_description = 'Photos'
    
    def get_queryset(self, request):
        """Optimize queryset for better performance"""
        return super().get_queryset(request).select_related()


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_class', 'date', 'venue', 'organizer', 'participant_range', 'schedule_status', 'created_at']
    list_filter = ['schedule_status', 'event_class', 'date', 'organizer', 'venue']
    search_fields = ['title', 'description', 'venue__venue', 'event_class__event_name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'event_class', 'organizer')
        }),
        ('Event Details', {
            'fields': ('date', 'venue', 'number_of_participants_lowerbound', 'number_of_participants_upperbound')
        }),
        ('Status', {
            'fields': ('schedule_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def participant_range(self, obj):
        """Display participant range in list view"""
        if obj.number_of_participants_lowerbound and obj.number_of_participants_upperbound:
            return f"{obj.number_of_participants_lowerbound}-{obj.number_of_participants_upperbound}"
        elif obj.number_of_participants_lowerbound:
            return f"{obj.number_of_participants_lowerbound}+"
        elif obj.number_of_participants_upperbound:
            return f"≤{obj.number_of_participants_upperbound}"
        return "-"
    participant_range.short_description = 'Participants'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registered_at']
    list_filter = ['event', 'registered_at']
    search_fields = ['user__username', 'user__email', 'event__title']
    date_hierarchy = 'registered_at'
    readonly_fields = ['registered_at']
    fieldsets = (
        ('Registration Details', {
            'fields': ('event', 'user', 'notes')
        }),
        ('Timestamp', {
            'fields': ('registered_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'event_organization', 
        'event_type', 
        'event_datetime_begin', 
        'duration_hours', 
        'event_area', 
        'people_range', 
        'status', 
        'created_at'
    ]
    list_filter = ['status', 'event_type', 'event_area', 'event_datetime_begin']
    search_fields = ['event_organization', 'event_type', 'event_area', 'event_specialrequests']
    date_hierarchy = 'event_datetime_begin'
    readonly_fields = ['created_at', 'updated_at', 'event_datetime_end', 'duration_hours']
    
    fieldsets = (
        ('Event Details', {
            'fields': (
                'event_organization', 
                'event_type', 
                'event_datetime_begin', 
                'event_datetime_delta',
                'event_area'
            )
        }),
        ('Capacity', {
            'fields': (
                'event_number_of_people_min', 
                'event_number_of_people_max'
            )
        }),
        ('Additional Information', {
            'fields': ('event_specialrequests', 'status')
        }),
        ('Calculated Fields', {
            'fields': ('event_datetime_end', 'duration_hours'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def people_range(self, obj):
        """Display people range in list view"""
        return f"{obj.event_number_of_people_min}-{obj.event_number_of_people_max}"
    people_range.short_description = 'People Range'
    
    def duration_hours(self, obj):
        """Display duration in hours"""
        return f"{obj.duration_hours:.1f}h"
    duration_hours.short_description = 'Duration'
