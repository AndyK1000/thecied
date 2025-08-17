from django.contrib import admin
from .models import Suites, SuiteOperatingModels, SuiteContracts, SuitePhoto


class SuitePhotoInline(admin.TabularInline):
    model = SuitePhoto
    extra = 3
    fields = ['image', 'caption']


@admin.register(Suites)
class SuitesAdmin(admin.ModelAdmin):
    list_display = ['suite_id', 'suite_number', 'whiteboard', 'filing_cabinet', 'height_adjustible_desk', 'office_chairs', 'corner_unit', 'minifridge']
    list_filter = ['whiteboard', 'filing_cabinet', 'corner_unit', 'minifridge']
    search_fields = ['suite_id', 'suite_number']
    ordering = ['suite_number']
    inlines = [SuitePhotoInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('suite_number', 'floor_plan')
        }),
        ('Suite Features', {
            'fields': ('whiteboard', 'filing_cabinet', 'height_adjustible_desk', 'office_chairs', 'corner_unit', 'minifridge')
        }),
    )


@admin.register(SuitePhoto)
class SuitePhotoAdmin(admin.ModelAdmin):
    list_display = ['suite', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at', 'suite']
    search_fields = ['suite__suite_number', 'caption']


@admin.register(SuiteOperatingModels)
class SuiteOperatingModelsAdmin(admin.ModelAdmin):
    list_display = ['model_id', 'model_name', 'is_shared', 'pricepoint', 'period']
    list_filter = ['is_shared']
    search_fields = ['model_name']
    ordering = ['model_name']
    
    def period(self, obj):
        return f"{obj.period} days"
    period.short_description = 'Pricing Period'


@admin.register(SuiteContracts)
class SuiteContractsAdmin(admin.ModelAdmin):
    list_display = ['roe_id', 'suite', 'entity', 'model', 'roe_begin', 'roe_end', 'on_going']
    list_filter = ['roe_begin', 'roe_end', 'on_going', 'individual', 'organization']
    search_fields = ['suite__suite_number']
    ordering = ['-roe_begin']
    
    fieldsets = (
        ('Contract Details', {
            'fields': ('suite', 'model')
        }),
        ('Entity Information', {
            'fields': ('individual', 'organization'),
            'description': 'Select either an individual OR an organization (not both)'
        }),
        ('Contract Duration', {
            'fields': ('roe_begin', 'on_going', 'roe_end'),
            'description': 'If "On going" is checked, the end date is not required'
        }),
    )
    
    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/core.js',
            'admin/js/contract_admin.js',
        )
        css = {
            'all': ('admin/css/widgets.css',)
        }
    
    def entity(self, obj):
        return str(obj.get_entity())
    entity.short_description = 'Entity'
