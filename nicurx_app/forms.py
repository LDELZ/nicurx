from django.forms import ModelForm
from django import forms
from .models import Medication, Patient, MedicationProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#create class for project form
class PatientForm(ModelForm):
        class Meta:
                model = Patient
                fields =('is_active', 'first_name', 'last_name', 'id_number', 'guardian_name', 'date_of_birth', 'weight', 'height', 'medication_profile')
                widgets = {
                    'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
                }
