from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
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
   active_patients = Patient.objects.filter(is_active=True)
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