# Fundamental imports
import os
from django.shortcuts import render, redirect

# User authentication imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .decorators import allowed_users

# Dependency imports
from django.utils import timezone
from django.views import generic
from django.contrib import messages
from django.contrib.auth.models import Group
from django.conf import settings
from django.templatetags.static import static
from django.db.models import Count

# Model/ form imports
from .models import *
from .forms import PatientForm, CreateUserForm, SupervisorForm, MedicationForm, ProfileForm

# ReportLab imports
from django.http import HttpResponse
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, black
from reportlab.graphics.barcode import qr

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
            medications_with_doses = MedicationDosage.objects.filter(profile=patient.medication_profile).select_related('medication')

            medications_context = []
            for local_medication in medications_with_doses:
                calculated_dose = local_medication.medication.dose_limit * patient.weight
                medication_info = {
                    'medication_name': local_medication.medication.medication_name,
                    'dose': local_medication.dose,
                    'dose_limit': local_medication.medication.dose_limit,
                    'calculated_dose': calculated_dose,
                    'issue': calculated_dose > local_medication.medication.dose_limit
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
# Search Bar implementation
def patient_search(request):
    id_number_lookup = request.GET.get('id_number')
    try:
        patient = Patient.objects.get(id_number=id_number_lookup)
        return redirect(patient.get_absolute_url())
    except Patient.DoesNotExist:
        messages.error(request, "No patients with that ID number exist")
        return redirect('guardian-search')
    
# PDF and QR Code implementation
class PatientPDFView(generic.DetailView):
   # Define base model as the patient model; most information will come from this model
   # Additional methods will gather information from related models
   model = Patient

   # Method to get all details about related medication profile, associated medications, and associated doses
   # This method is required to setup the context of information associated with the patient
   # It is similar to the Patient Detail View, though the variables will be used to draw the PDF instead
   def get_medication_details(self, patient):
      
      # Create an empty list to store the medications associated with this patient
      medications_with_doses = []

      # Test if the patient has an assigned medication profile; this is not mandatory since patients cannot be created
      # without assigning a medication profile. I included this test in case that requirement is removed later
      if patient.medication_profile:

         # Query the database for MedicationDosage objects and filter if they match the current patient's medication profile ID
         # Assign those matching medications to the list of medication_with_doses
         # This is required because each patient's medication profile will have different doses related only to them and are generated procedurally
         medications_with_doses = MedicationDosage.objects.filter(profile=patient.medication_profile).select_related('medication')

         # Declare a new list to store the context data for each medication associated with this patient's profile
         medications_context = []

         # Iterate through the list of medications_with_doses and retrieve all information to be displayed on the PDF
         for local_medication in medications_with_doses:
            calculated_dose = local_medication.medication.dose_limit * patient.weight
            medication_info = {
               'medication_name': local_medication.medication.medication_name,
               'dose': local_medication.dose,
               'dose_limit': local_medication.medication.dose_limit,
               'calculated_dose': calculated_dose,
               'issue': local_medication.dose > calculated_dose
            }

            # Append the newly defined information to the medications_context list, finalizing the list with all necessary information
            # This allows for the view to retrieve information by variable name when generating the PDF
            medications_context.append(medication_info)

      return medications_context

   # Define a new method to handle when the user clicks the PDF download button; handles server GET method initiated
   def get(self, request, *args, **kwargs):
         
         # Define a new patient variable and call the get_details method above to get the context information for this patient
         patient = self.get_object()
         medications_details = self.get_medication_details(patient)

         # Inform the browser that the response should be handled as a PDF file
         # Then inform it to handle the response as a downloadable file with a pdf extension
         response = HttpResponse(content_type='application/pdf')
         response['Content-Disposition'] = 'attachment; filename="patient_info.pdf"'

         # Generate a new PDF canvas using the Canvas class from ReportLab using Letter paper size
         # Assign it to a new variable to direct all draw commands to (this renders text and images to the page)
         new_pdf = canvas.Canvas(response, pagesize=letter)         
         page_width, page_height = letter         

         # Print the company logo at the top
         image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'brand.png')
         image_x_pos = 100
         image_y_pos = 670
         new_pdf.drawImage(image_path, image_x_pos, image_y_pos, width=400, height=80)

         # PDF Page title header - displays "Detailed Patient Report" under logo"
         custom_color = Color(0.106,0.259,0.361)
         pdf_render_y_position = 650
         pdf_render_x_position = 220
         new_pdf.setFont("Helvetica-Bold", 16)
         new_pdf.setFillColor(custom_color)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Detailed Patient Report")

         # Set new variables for draw position (pixel offset from PDF page border)
         pdf_render_x_position = 50
         render_position_change = 20
        
         # Print the details
         # HEADER: Patient personal information title
         pdf_render_y_position -= render_position_change * 2
         new_pdf.setFont("Helvetica-Bold", 14)
         new_pdf.setFillColor(black)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Personal Information")

         # BODY: Patient personal information
         pdf_render_x_position = 100
         pdf_render_y_position -= render_position_change
         new_pdf.setFont("Helvetica", 12)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Patient Name: {patient.first_name} {patient.last_name}")

         pdf_render_y_position -= render_position_change
         new_pdf.drawString(100, pdf_render_y_position, f"ID Number: {patient.id_number}")

         pdf_render_y_position -= render_position_change
         new_pdf.drawString(100, pdf_render_y_position, f"Date of Birth: {patient.date_of_birth}")

         pdf_render_y_position -= render_position_change
         new_pdf.drawString(100, pdf_render_y_position, f"Guardian Name: {patient.guardian_name}")
         
         # HEADER: Patient body metrics
         pdf_render_x_position = 50
         pdf_render_y_position -= render_position_change * 2
         new_pdf.setFont("Helvetica-Bold", 14)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Body Metrics")

         # BODY: Patient body metrics
         pdf_render_y_position -= render_position_change
         pdf_render_x_position = 100
         new_pdf.setFont("Helvetica", 12)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Weight (kg): {patient.weight}")

         pdf_render_y_position -= render_position_change
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Height (cm): {patient.height}")

         pdf_render_y_position -= render_position_change
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"BSA (m^2): {patient.calculate_bsa():.2f}")

         # HEADER: Medication profile title
         pdf_render_x_position = 50
         pdf_render_y_position -= render_position_change * 2
         new_pdf.setFont("Helvetica-Bold", 14)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, "Medication Profile:")

         # BODY: Medication profile title
         pdf_render_y_position -= render_position_change
         pdf_render_x_position = 100
         new_pdf.setFont("Helvetica", 12)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Profile: { patient.medication_profile.title }")

         # BODY: Medication issues
         pdf_render_y_position -= render_position_change
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, f"Active Issues: { patient.medication_profile.number_medications() }")

         # HEADER: Medications title
         pdf_render_x_position = 50
         pdf_render_y_position -= render_position_change * 2
         new_pdf.setFont("Helvetica-Bold", 14)
         new_pdf.drawString(pdf_render_x_position, pdf_render_y_position, "Medications:")
         
         # BODY: Display the medication details associated with the patient's medication profile
         new_pdf.setFont("Helvetica", 12)
         for medication in medications_details:
            pdf_render_y_position -= render_position_change
            new_pdf.drawString(120, pdf_render_y_position, f"Medication: {medication['medication_name']} {medication['dose']} mg:  {'Warning!' if medication['issue'] else 'No issues'}")

         # QR Code drawing
         # Build a new string representing the absolute URL for the patient detail page
         server_url = 'http://127.0.0.1:8000'
         url = server_url + '/patient/' + str(patient.id)

         # Encode the string as a QR Code widget using ReportLab
         qr_code = qr.QrCodeWidget(url)

         dimension = 200
         qr_code.barWidth = dimension
         qr_code.barHeight = dimension

         image_qr_code = Drawing(dimension, dimension)
         image_qr_code.add(qr_code)
         
         pdf_render_x_position = page_width - 210
         pdf_render_y_position = 10
         renderPDF.draw(image_qr_code, new_pdf, pdf_render_x_position, pdf_render_y_position)

         # Display the URL text beneath the QR Code for people who can't scan it
         new_pdf.setFont("Helvetica", 10)
         new_pdf.setFillColor(black)
         new_pdf.drawString(pdf_render_x_position+28, pdf_render_y_position+12, f"{url}")

         # Show the PDF page in a new browser window
         new_pdf.showPage()

         # Save the PDF to the browser's download folder
         new_pdf.save()

         return response
#--------------------------------------------------------------------------------------------