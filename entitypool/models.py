from django.db import models


class Individuals(models.Model):
    ui_id = models.AutoField(primary_key=True)
    name_first = models.CharField(max_length=100)
    name_last = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number1 = models.CharField(max_length=20, null=True, blank=True)
    phone_number2 = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    photo = models.ImageField(upload_to='individual_photos/', null=True, blank=True, help_text='Upload individual photo')
    rf_id = models.CharField(max_length=100, null=True, blank=True)
    key_id = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        verbose_name = "Individual"
        verbose_name_plural = "Individuals"
    
    def __str__(self):
        return f"{self.name_first} {self.name_last}"


class Organizations(models.Model):
    uo_id = models.AutoField(primary_key=True)
    organization_name = models.CharField(max_length=200)
    organization_ein = models.CharField(max_length=20)
    organization_info = models.TextField()
    logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True, help_text='Upload organization logo')
    
    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
    
    def __str__(self):
        return self.organization_name
