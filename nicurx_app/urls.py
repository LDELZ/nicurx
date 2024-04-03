from django.urls import path
from django.contrib import admin
from .views import accessibility_view, disclaimer_view
from . import views

urlpatterns = [
#path function defines a url pattern
#'' is empty to represent based path to app
# views.index is the function defined in views.py
# name='index' parameter is to dynamically create url
# example in html <a href="{% url 'index' %}">Home</a>.
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('accessibility/', accessibility_view, name='accessibility'),
    path('disclaimer/', disclaimer_view, name='disclaimer'),
]
