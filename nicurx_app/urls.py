from django.urls import path
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
]
