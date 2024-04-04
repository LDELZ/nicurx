from django.db import models
from django.urls import reverse
import math

# Create your models here.
class Medication(models.Model):

    CalculationUnit = (
    ('KG', 'Kilograms'),
    ('BSA', 'Body Mass Index'),
    ('None', 'None'),
    )
    medication_name = models.CharField(max_length=200)
    calculation_unit = models.CharField(max_length=200, choices=CalculationUnit, blank = False, default=None)

    def __str__(self):
        return self.medication_name
    
    def get_absolute_url(self):
        return reverse('medication-detail', args=[str(self.id)])
    
class MedicationProfile(models.Model):

    def get_absolute_url(self):
        return reverse('medication-profile-detail', args=[str(self.id)])
    
class Patient(models.Model):
    is_active = models.BooleanField(default = False)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    id_number = models.IntegerField(null=True)
    guardian_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    weight = models.FloatField(help_text="Weight in kilograms", default=1.0)
    height = models.FloatField(help_text="Height in centimeters", default=1.0)
    def calculate_bsa(self):
        if self.weight > 0 and self.height > 0:
            return math.sqrt((self.height * self.weight) / 3600)
        else:
            return 0
    def __str__(self):
        return self.last_name

    def get_absolute_url(self):
        return reverse('patient-detail', args=[str(self.id)])
