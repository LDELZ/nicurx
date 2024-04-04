from django.contrib import admin

# Register your models here.
from .models import Medication, Patient, MedicationProfile
admin.site.register(Medication)
admin.site.register(Patient)
admin.site.register(MedicationProfile)
