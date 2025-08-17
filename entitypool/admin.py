from django.contrib import admin
from .models import Individuals, Organizations


@admin.register(Individuals)
class IndividualsAdmin(admin.ModelAdmin):
    list_display = ['ui_id', 'name_first', 'name_last', 'email', 'dob', 'phone_number1', 'has_photo']
    list_filter = ['dob']
    search_fields = ['name_first', 'name_last', 'email', 'phone_number1', 'phone_number2']
    ordering = ['name_last', 'name_first']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name_first', 'name_last', 'dob', 'photo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number1', 'phone_number2', 'address')
        }),
        ('Access Information', {
            'fields': ('rf_id', 'key_id')
        }),
    )
    
    class Media:
        js = (
            'admin/js/contract_admin.js',
        )
    
    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = 'Photo'


@admin.register(Organizations)
class OrganizationsAdmin(admin.ModelAdmin):
    list_display = ['uo_id', 'organization_name', 'organization_ein', 'has_logo']
    search_fields = ['organization_name', 'organization_ein']
    ordering = ['organization_name']
    
    fieldsets = (
        ('Organization Details', {
            'fields': ('organization_name', 'organization_ein', 'logo')
        }),
        ('Additional Information', {
            'fields': ('organization_info',)
        }),
    )
    
    class Media:
        js = (
            'admin/js/contract_admin.js',
        )
    
    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'Logo'
