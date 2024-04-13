from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
#path function defines a url pattern
#'' is empty to represent based path to app
# views.index is the function defined in views.py
# name='index' parameter is to dynamically create url
# example in html <a href="{% url 'index' %}">Home</a>.
path('', views.index, name='index'),
path('admin/', admin.site.urls),
path('accessibility/', views.accessibility_view, name='accessibility'),
path('disclaimer/', views.disclaimer_view, name='disclaimer'),
path('supervisor_login/', views.supervisor_login_view, name='supervisor_login'),
path('contact_info/', views.contact_info_view, name='supervisor_login'),
path('patient_list/', views.patient_list_view, name='patient_list'),
path('patient_grid/', views.patient_grid_view, name='patient_grid'),
path('patient_grid_ID/', views.patient_grid_view_ID, name='patient_grid_ID'),
path('patient_grid_status/', views.patient_grid_view_status, name='patient_grid_status'),
path('patient_history/', views.patient_grid_view_all, name='patient_history'),
path('patient_history_ID/', views.patient_grid_view_all_ID, name='patient_history_ID'),
path('patient_history_date/', views.patient_grid_view_all_date, name='patient_history_date'),
path('patient/<int:pk>', views.PatientDetailView.as_view(), name='patient-detail'),
path('patient/<int:patient_id>/', views.updatePatient, name='update-patient'),
path('patient/create_patient/', views.createPatient, name='create-patient'),
path('patient/discharge_patient/<int:patient_id>', views.dischargePatient, name='discharge-patient'),
path('patient/delete_patient/<int:patient_id>', views.deletePatient, name='delete-patient'),
path('profile_grid/', views.profile_grid_view, name='profile_grid'),
path('profile_grid_ID/', views.profile_grid_view_ID, name='profile_grid_ID'),
path('profile/<int:pk>', views.ProfileDetailView.as_view(), name='profile-detail'),

# user accounts
path('accounts/', include('django.contrib.auth.urls')),
path('accounts/register/', views.registerPage, name='register_page'),

path('patient/<int:pk>/pdf/', views.PatientPDFView.as_view(), name='patient-pdf'),
]
