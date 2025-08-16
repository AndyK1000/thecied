from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'organizer', 'is_active', 'created_at']
    list_filter = ['is_active', 'date', 'organizer']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'organizer')
        }),
        ('Event Details', {
            'fields': ('date', 'location', 'max_participants', 'registration_deadline')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


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
