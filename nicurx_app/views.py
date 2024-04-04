from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.utils import timezone
from django.views import generic
from .forms import PatientForm

# Create your views here.
def index(request):
    # Render index.html
    return render( request, 'nicurx_app/index.html')

def accessibility_view(request):
    return render(request, 'nicurx_app/accessibility.html')

def disclaimer_view(request):
    return render(request, 'nicurx_app/disclaimer.html')

def supervisor_login_view(request):
    return render(request, 'nicurx_app/supervisor_login.html')

def contact_info_view(request):
    return render(request, 'nicurx_app/contact_info.html')

def patient_list_view(request):
   active_patients = Patient.objects.filter(is_active=True).order_by('last_name')
   print("active patient query set", active_patients)
   return render( request, 'nicurx_app/patient_list.html', {'active_patients':active_patients})

def profile_grid_view(request):
   profiles = MedicationProfile.objects.filter(is_active=True).order_by('title')
   print("profile query set", profiles)
   return render( request, 'nicurx_app/medication_profiles.html', {'profiles':profiles})

def profile_grid_view_ID(request):
   profiles = MedicationProfile.objects.filter(is_active=True).order_by('id_number')
   print("profile query set", profiles)
   return render( request, 'nicurx_app/medication_profiles.html', {'profiles':profiles})

def patient_grid_view(request):
   active_patients = Patient.objects.filter(is_active=True).order_by('last_name')
   print("active patient query set", active_patients)
   return render( request, 'nicurx_app/patient_grid.html', {'active_patients':active_patients})

def patient_grid_view_ID(request):
   active_patients = Patient.objects.filter(is_active=True).order_by('id_number')
   print("active patient query set", active_patients)
   return render( request, 'nicurx_app/patient_grid.html', {'active_patients':active_patients})

def patient_grid_view_status(request):
    active_patients = Patient.objects.filter(is_active=True).select_related('medication_profile')
    sorted_active_patients = sorted(active_patients, key=lambda p: getattr(p.medication_profile, 'has_issues', False), reverse=True)
    return render(request, 'nicurx_app/patient_grid.html', {'active_patients': sorted_active_patients})

def patient_grid_view_all(request):
   active_patients = Patient.objects.filter(is_active=False).order_by('last_name')
   print("active patient query set", active_patients)
   return render( request, 'nicurx_app/patient_history.html', {'active_patients':active_patients})

def patient_grid_view_all_ID(request):
   active_patients = Patient.objects.filter(is_active=False).order_by('id_number')
   print("active patient query set", active_patients)
   return render( request, 'nicurx_app/patient_history.html', {'active_patients':active_patients})

def patient_grid_view_all_date(request):
   active_patients = Patient.objects.filter(is_active=False).order_by('discharge_date')
   print("active patient query set", active_patients)
   return render( request, 'nicurx_app/patient_history.html', {'active_patients':active_patients})

class PatientDetailView(generic.DetailView):
   model = Patient
   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      return context
   
# View to generate a form to update a portfolio 
def updatePatient(request, patient_id):
   patient = Patient.objects.get(pk=patient_id)

   if request.method == 'POST':
      form = PatientForm(request.POST, instance=patient)
      if form.is_valid():
         form.save()

         # Redirect back to the portfolio detail page
         return redirect('patient-detail', pk=patient_id)
   else:
      form = PatientForm(instance=patient)
   context = {'form': form, 'patient': patient}
   return render(request, 'nicurx_app/update_form.html', context)

def createPatient(request):
   
   # Display the default form the first time it is being requested (used for creation)
   form = PatientForm()

   # Test if the form submission is to POST
   if request.method == 'POST':

      # Create a new dictionary with form data and portfolio_id
      form = PatientForm(request.POST)

      # Test if the form contents are valid
      if form.is_valid():

         # Save the form without committing to the database
         patient = form.save()


         # Redirect back to the portfolio detail page
         return redirect('patient-detail', patient.pk)
      
   # Redirect back to the update_form URL
   context = {'form': form}
   return render(request, 'nicurx_app/update_form.html', context)

# View to generate a form to delete a patient
def dischargePatient(request, patient_id):

   patient = Patient.objects.get(pk=patient_id)
   if request.method == 'POST':
      patient.is_active = False
      patient.discharge_date = timezone.now()
      patient.save()
      return redirect('patient_list')
   
   context = {'patient': patient}
   # Redirect back to the portfolio detail page
   return render(request, 'nicurx_app/patient_discharge.html', context)

class ProfileDetailView(generic.DetailView):
   model = MedicationProfile
   # We need to extend the context of 
   # Overridden method to get more context to the template, kwargs gives the function an unknown number of key-value pairs
   def get_context_data(self, **kwargs):

      # Get the context data of the superclass (DetailView) for all keywords in the dictionary
      context = super().get_context_data(**kwargs)

      # Assign the portfolio current portfolio key to a variable portfolio
      # Use that portfolio key to access the projects associated with it to define a new context 'projects' 
      profile = context['object']
      context['medications'] = profile.medications.all()
      return context
   
# View to generate a form to delete a project 
def deletePatient(request, patient_id):

   # Get the current project and portfolio objects from their IDs in the URL
   patient = Patient.objects.get(pk=patient_id)

   if request.method == 'POST':
      patient.delete()
      return redirect('patient_list')
   
   context = {'patient': patient}
   # Redirect back to the portfolio detail page
   return render(request, 'nicurx_app/patient_delete.html', context)