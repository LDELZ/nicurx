from django.db import models
from django.urls import reverse
import math

# Create your models here.  
class MedicationProfile(models.Model):
    title = models.CharField(max_length=200, blank = False, default=None)
    about = models.TextField(blank = True)
    id_number = models.IntegerField(null=True)
    is_active = models.BooleanField(default = True)
    has_issues = models.BooleanField(default = False)
    def number_medications(self):
        return self.medications.count()
    
    def has_high_risk_med(self):
        return self.medications.filter(high_risk=True).exists()
    
    #Define default String to return the name for representing the Model object."
    def __str__(self):
        return self.title

    #Returns the URL to access a particular instance of MyModelName.
    def get_absolute_url(self):
        return reverse('medication-profile-detail', args=[str(self.id)])
    
class Patient(models.Model):
    is_active = models.BooleanField(default = True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    id_number = models.IntegerField(null=True)
    guardian_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    weight = models.FloatField(help_text="Weight in kilograms", default=1.0)
    height = models.FloatField(help_text="Height in centimeters", default=1.0)
    medication_profile = models.OneToOneField(MedicationProfile, on_delete=models.CASCADE, default=None, null=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    def calculate_bsa(self):
        if self.weight > 0 and self.height > 0:
            return math.sqrt((self.height * self.weight) / 3600)
        else:
            return 0
    def __str__(self):
        return self.last_name

    def get_absolute_url(self):
        return reverse('patient-detail', args=[str(self.id)])

class Medication(models.Model):

    CalculationUnit = (
    ('KG', 'Kilograms'),
    ('BSA', 'Body Mass Index'),
    ('Rate', 'Rate'),
    ('None', 'None'),
    )
    medication_name = models.CharField(max_length=200)
    calculation_unit = models.CharField(max_length=200, choices=CalculationUnit, blank = False, default=None)
    medication_profile = models.ForeignKey(MedicationProfile, on_delete=models.CASCADE, related_name='medications', default=None, null=True)
    resource_link = models.TextField(blank = True)
    evidence_description = models.TextField(blank = True)
    high_risk = models.BooleanField(default = False)
    def __str__(self):
        return self.medication_name
    
    def get_absolute_url(self):
        return reverse('medication-detail', args=[str(self.id)])