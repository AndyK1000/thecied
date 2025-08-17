from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from entitypool.models import Organizations, Individuals


class SuitePhoto(models.Model):
    suite = models.ForeignKey('Suites', on_delete=models.CASCADE, related_name='suite_photos')
    image = models.ImageField(upload_to='suite_photos/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Suite Photo"
        verbose_name_plural = "Suite Photos"
    
    def __str__(self):
        return f"Photo for Suite {self.suite.suite_number}"


class Suites(models.Model):
    suite_id = models.AutoField(primary_key=True)
    suite_number = models.CharField(max_length=20)
    floor_plan = models.FileField(upload_to='suite_floorplans/', null=True, blank=True, help_text='Upload PDF floor plan')
    
    # Suite features
    whiteboard = models.BooleanField(default=False)
    filing_cabinet = models.BooleanField(default=False)
    height_adjustible_desk = models.IntegerField(default=0, help_text='Number of height adjustable desks')
    office_chairs = models.IntegerField(default=0, help_text='Number of office chairs')
    corner_unit = models.BooleanField(default=False)
    minifridge = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Suite"
        verbose_name_plural = "Suites"
    
    def __str__(self):
        return f"Suite {self.suite_number}"


class SuiteOperatingModels(models.Model):
    model_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=100)
    is_shared = models.BooleanField(default=False)
    pricepoint = models.DecimalField(max_digits=10, decimal_places=2, default=3000.00, help_text='Price in dollars')
    period = models.IntegerField(default=180, help_text='Time period in days for the pricing')
    
    class Meta:
        verbose_name = "Suite Operating Model"
        verbose_name_plural = "Suite Operating Models"
    
    def __str__(self):
        return self.model_name


class SuiteContracts(models.Model):
    roe_id = models.AutoField(primary_key=True)
    suite = models.ForeignKey(Suites, on_delete=models.CASCADE)
    
    # Direct foreign keys to handle both Organizations and Individuals
    individual = models.ForeignKey(Individuals, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE, null=True, blank=True)
    
    model = models.ForeignKey(SuiteOperatingModels, on_delete=models.CASCADE)
    roe_begin = models.DateField()
    roe_end = models.DateField(null=True, blank=True)
    on_going = models.BooleanField(default=False, help_text='Check if this is an ongoing contract (no end date)')
    
    class Meta:
        verbose_name = "Suite Contract"
        verbose_name_plural = "Suite Contracts"
    
    def __str__(self):
        return f"Contract {self.roe_id} - Suite {self.suite.suite_number}"
    
    def clean(self):
        """Custom validation for the model"""
        super().clean()
        
        # Ensure exactly one entity is selected
        if not self.individual and not self.organization:
            raise ValidationError('You must select either an individual or an organization.')
        
        if self.individual and self.organization:
            raise ValidationError('You cannot select both an individual and an organization. Choose one.')
        
        # Ensure end date is provided if not ongoing
        if not self.on_going and not self.roe_end:
            raise ValidationError('End date is required unless the contract is ongoing.')
        
        # Ensure end date is after start date
        if self.roe_end and self.roe_begin and self.roe_end <= self.roe_begin:
            raise ValidationError('End date must be after start date.')
    
    def get_entity(self):
        """Return the associated individual or organization"""
        if self.individual:
            return self.individual
        elif self.organization:
            return self.organization
        return None
