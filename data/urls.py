from __future__ import unicode_literals

from django.urls import path
from . import views


app_name = 'data'
urlpatterns = [
   
    path('', views.home, name='home'),
 
]
