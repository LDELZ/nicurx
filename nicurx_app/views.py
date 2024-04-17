from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.utils import timezone
from django.views import generic
from .forms import PatientForm, CreateUserForm, SupervisorForm, MedicationForm, ProfileForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import logout
import os
from reportlab.lib.colors import Color, black
from django.conf import settings
from django.templatetags.static import static
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from django.db.models import Count

# User authentication views
#--------------------------------------------------------------------------------------------
def registerPage(request):
   form = CreateUserForm()
   if request.method == 'POST':
      form = CreateUserForm(request.POST)
      if form.is_valid():
         user = form.save()
         username = form.cleaned_data.get('username')
         group = Group.objects.get(name='supervisor')
         user.groups.add(group)
         supervisor = Supervisor.objects.create(user=user,)
         supervisor.save()

         messages.success(request, 'Account was created for ' + username)
         return redirect('login')
   
   context = {'form':form}
   return render(request, 'registration/register.html', context)

def logout_view(request):
    logout(request)
    return render(request, 'registration/logout.html')

def password_reset_view(request):
    return render(request, 'registration/password_reset_form.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['supervisor'])
def userPage(request):
   supervisor = request.user.supervisor
   form = SupervisorForm(instance = supervisor)
   print('supervisor', supervisor)
   if request.method == 'POST':
      form = SupervisorForm(request.POST, request.FILES, instance=supervisor)
      if form.is_valid():
         form.save()
   context = {'form':form}
   return render(request, 'nicurx_app/user.html', context)
#--------------------------------------------------------------------------------------------


# General navigation:
#--------------------------------------------------------------------------------------------
def index(request):
    return render( request, 'nicurx_app/index.html')

def guardian_view(request):
    return render( request, 'nicurx_app/guardian_search.html')

def accessibility_view(request):
    return render(request, 'nicurx_app/accessibility.html')

def disclaimer_view(request):
    return render(request, 'nicurx_app/disclaimer.html')

def supervisor_login_view(request):
    return render(request, 'nicurx_app/supervisor_login.html')

def contact_info_view(request):
    return render(request, 'nicurx_app/contact_info.html')
#--------------------------------------------------------------------------------------------


# Patient views
#--------------------------------------------------------------------------------------------
def patient_list_view(request):
   active_patients = Patient.objects.filter(is_active=True).order_by('last_name')
   print("active patient query set", active_patients)
   return render( request, 'nicurx_app/patient_list.html', {'active_patients':active_patients})

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
        patient = context['object']

        if patient.medication_profile:
            medications_with_doses = MedicationDosage.objects.filter(
                profile=patient.medication_profile).select_related('medication')

            medications_context = []
            for md in medications_with_doses:
                calculated_dose = md.medication.dose_limit * patient.weight
                medication_info = {
                    'medication_name': md.medication.medication_name,
                    'dose': md.dose,
                    'dose_limit': md.medication.dose_limit,
                    'calculated_dose': calculated_dose,
                    'issue': calculated_dose > md.medication.dose_limit
                }
                medications_context.append(medication_info)

            context['medications_with_doses'] = medications_context
            patient.medication_profile.update_issues()

        else:
            context['medications_with_doses'] = []

        return context

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
#--------------------------------------------------------------------------------------------


# Profile views
#--------------------------------------------------------------------------------------------
def profile_grid_view(request):
   profiles = MedicationProfile.objects.filter(is_active=True).annotate(medication_count=Count('medications')).order_by('title')
   return render(request, 'nicurx_app/medication_profiles.html', {'profiles': profiles})


def profile_grid_view_ID(request):
   profiles = MedicationProfile.objects.filter(is_active=True).order_by('id_number')
   print("profile query set", profiles)
   return render( request, 'nicurx_app/medication_profiles.html', {'profiles':profiles})

def profileDetail(request, profile_id):
   profile = MedicationProfile.objects.get(pk=profile_id)
   medications_with_doses = MedicationDosage.objects.filter(profile=profile)
   profile.refresh_from_db()
   context = {
      'profile': profile,
      'medications_with_doses': medications_with_doses
   }
   return render(request, 'nicurx_app/medicationprofile_detail.html', context)


def createProfile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)

        if form.is_valid():
            profile = form.save(commit=True)
            profile.save()

            # Display checkpoxes for each medication
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('medication_') and value:
                    medication_id = int(field_name.split('_')[1])
                    medication = Medication.objects.get(id=medication_id)
                    profile.medications.add(medication)
            
            return redirect('profile-detail', profile_id=profile.pk)
    else:
        form = ProfileForm()

    context = {'form': form}
    return render(request, 'nicurx_app/profile_form.html', context)


def updateProfile(request, profile_id):
    profile = MedicationProfile.objects.get(pk=profile_id)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            
            for medication in Medication.objects.all():
                checkbox_field_name = f'medication_{medication.id}'
                float_field_name = f'dosage_{medication.id}'

                if form.cleaned_data[checkbox_field_name]:
                    dosage_value = form.cleaned_data[float_field_name]
                    MedicationDosage.objects.update_or_create(
                        profile=profile, 
                        medication=medication,
                        defaults={'dose': dosage_value}
                    )
                else:
                    MedicationDosage.objects.filter(profile=profile, medication=medication).delete()

            return redirect('profile-detail', profile_id=profile_id)

    else:
        form = ProfileForm(instance=profile)

    context = {'form': form, 'profile': profile}
    return render(request, 'nicurx_app/profile_update.html', context)


def deleteProfile(request, profile_id):
   profile = MedicationProfile.objects.get(pk=profile_id)
   medications_with_doses = MedicationDosage.objects.filter(profile=profile)
   if request.method == 'POST':
      profile.delete()
      return redirect('profile_grid')
   
   context = {
      'profile': profile,
      'medications_with_doses': medications_with_doses
   }
   # Redirect back to the portfolio detail page
   return render(request, 'nicurx_app/profile_delete.html', context)
#--------------------------------------------------------------------------------------------


# Medication views
#--------------------------------------------------------------------------------------------
def medication_list_view(request):
   active_medications = Medication.objects.order_by('medication_name')
   print("active patient query set", active_medications)
   return render( request, 'nicurx_app/medication_list.html', {'active_medications':active_medications})

class MedicationDetailView(generic.DetailView):
   model = Medication

@login_required(login_url='login')
@allowed_users(allowed_roles=['supervisor'])
def createMedication(request):
   
   # Display the default form the first time it is being requested (used for creation)
   form = MedicationForm()

   # Test if the form submission is to POST
   if request.method == 'POST':

      # Create a new dictionary with form data and portfolio_id
      form = MedicationForm(request.POST)

      # Test if the form contents are valid
      if form.is_valid():

         # Save the form without committing to the database
         medication = form.save()


         # Redirect back to the portfolio detail page
         return redirect('medication-detail', medication.pk)
      
   # Redirect back to the update_form URL
   context = {'form': form}
   return render(request, 'nicurx_app/medication_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['supervisor'])
def updateMedication(request, medication_id):
   medication = Medication.objects.get(pk=medication_id)

   if request.method == 'POST':
      form = MedicationForm(request.POST, instance=medication)
      if form.is_valid():
         form.save()

         # Redirect back to the portfolio detail page
         return redirect('medication-detail', pk=medication_id)
   else:
      form = MedicationForm(instance=medication)
   context = {'form': form, 'medication': medication}
   return render(request, 'nicurx_app/medication_update.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['supervisor'])
def deleteMedication(request, medication_id):

   # Get the current project and portfolio objects from their IDs in the URL
   medication = Medication.objects.get(pk=medication_id)

   if request.method == 'POST':
      medication.delete()
      return redirect('medication_list')
   
   context = {'medication': medication}
   # Redirect back to the portfolio detail page
   return render(request, 'nicurx_app/medication_delete.html', context)
#--------------------------------------------------------------------------------------------


# Exploration views
#--------------------------------------------------------------------------------------------
def patient_search(request):
    id_number = request.GET.get('id_number')
    try:
        patient = Patient.objects.get(id_number=id_number)
        return redirect(patient.get_absolute_url())
    except Patient.DoesNotExist:
        messages.error(request, "No patient with that ID number exists.")
        return redirect('guardian-search')
    
class PatientPDFView(generic.DetailView):
    model = Patient

    def get(self, request, *args, **kwargs):
         response = HttpResponse(content_type='application/pdf')
         response['Content-Disposition'] = 'attachment; filename="patient_info.pdf"'

         p = canvas.Canvas(response, pagesize=letter)         

         # Print the company logo
         image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'brand.png')
         p.drawImage(image_path, 100, 670, width=400, height=80)
         patient = self.get_object()
         medications = patient.medication_profile.medications.all() if patient.medication_profile else []

         url = 'http://127.0.0.1:8000/patient/' + str(patient.id)
         qr_code = qr.QrCodeWidget(url)
         bounds = qr_code.getBounds()
         qr_width = bounds[2] - bounds[0]
         qr_height = bounds[3] - bounds[1]

         d = Drawing(200, 200, transform=[200./qr_width, 0, 0, 200./qr_height, 0, 0])
         d.add(qr_code)
         page_width, page_height = letter
         x = page_width - 210
         y = 10
         renderPDF.draw(d, p, x, y)
         p.setFont("Helvetica", 10)
         p.setFillColor(black)
         p.drawString(x+28, y+12, f"{url}")

         custom_color = Color(0.106,0.259,0.361)
         y = 650
         x = 220

         # Print the header
         p.setFont("Helvetica-Bold", 16)
         p.setFillColor(custom_color)
         p.drawString(x, y, f"Detailed Patient Report")

         x = 50
         difference = 20
         # Print the details
         y -= difference * 2
         p.setFont("Helvetica-Bold", 14)
         p.setFillColor(black)
         p.drawString(x, y, f"Personal Information")

         x = 100
         y -= difference
         p.setFont("Helvetica", 12)
         p.drawString(x, y, f"Patient Name: {patient.first_name} {patient.last_name}")

         y -= difference
         p.drawString(100, y, f"ID Number: {patient.id_number}")

         y -= difference
         p.drawString(100, y, f"Date of Birth: {patient.date_of_birth}")

         y -= difference
         p.drawString(100, y, f"Guardian Name: {patient.guardian_name}")
         
         x = 50
         y -= difference * 2
         p.setFont("Helvetica-Bold", 14)
         p.drawString(x, y, f"Body Metrics")

         y -= difference
         x = 100
         p.setFont("Helvetica", 12)
         p.drawString(x, y, f"Weight (kg): {patient.weight}")

         y -= difference
         p.drawString(x, y, f"Height (cm): {patient.height}")

         y -= difference
         p.drawString(x, y, f"BSA (m^2): {patient.calculate_bsa():.2f}")

         x = 50
         y -= difference * 2
         p.setFont("Helvetica-Bold", 14)
         p.drawString(x, y, "Medication Profile:")

         y -= difference
         x = 100
         p.setFont("Helvetica", 12)
         p.drawString(x, y, f"Profile: { patient.medication_profile.title }")

         y -= difference
         p.drawString(x, y, f"Number of Medications: { patient.medication_profile.number_medications() }")

         y -= difference
         p.drawString(x, y, f"Active Issues: { patient.medication_profile.number_medications() }")

         x = 50
         y -= difference * 2
         p.setFont("Helvetica-Bold", 14)
         p.drawString(x, y, "Medications:")
         p.setFont("Helvetica", 12)
         for medication in medications:
            y -= 20
            p.drawString(120, y, f"{medication.medication_name}")

         p.showPage()
         p.save()

         return response
#--------------------------------------------------------------------------------------------