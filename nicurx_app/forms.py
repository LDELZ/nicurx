from django.forms import ModelForm
from django import forms
from .models import Medication, Patient, MedicationProfile, Supervisor, MedicationDosage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

#create class for project form
class PatientForm(ModelForm):
        class Meta:
                model = Patient
                fields =('is_active', 'first_name', 'last_name', 'id_number', 'guardian_name', 'date_of_birth', 'weight', 'height', 'medication_profile')
                widgets = {
                    'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
                }

class MedicationForm(ModelForm):
        class Meta:
                model = Medication
                fields ='__all__'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = MedicationProfile
        fields = '__all__'
        exclude = 'issues',

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        medications = Medication.objects.all()

        for medication in medications:
            checkbox_field_name = f'medication_{medication.id}'
            float_field_name = f'dosage_{medication.id}'
            
            if instance:
                is_selected = instance.medications.filter(id=medication.id).exists()
                dosage_instance = MedicationDosage.objects.filter(profile=instance, medication=medication).first()
                initial_dosage = dosage_instance.dose if dosage_instance else 0
            else:
                is_selected = False
                initial_dosage = 0

            self.fields[checkbox_field_name] = forms.BooleanField(
                required=False,
                label=f"{medication.medication_name}",
                initial=is_selected
            )
            self.fields[float_field_name] = forms.FloatField(
                required=False,
                label=f"Actual dose for {medication.medication_name} mg",
                initial=initial_dosage
            )


    def clean(self):
        cleaned_data = super().clean()
        medications = Medication.objects.all()
        for medication in medications:
            checkbox_field_name = f'medication_{medication.id}'
            float_field_name = f'dosage_{medication.id}'
            checkbox = cleaned_data.get(checkbox_field_name)
            dosage = cleaned_data.get(float_field_name)

            if checkbox and dosage is None:
                raise ValidationError(f"Dosage for {medication.medication_name} must be filled out if selected.")

        return cleaned_data

class CreateUserForm(UserCreationForm):
        class Meta:
                model = User
                fields = ['username', 'email', 'password1', 'password2']

class SupervisorForm(ModelForm):
        class Meta:
                model = Supervisor
                fields = '__all__'