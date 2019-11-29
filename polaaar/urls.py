from __future__ import unicode_literals
from django.urls import path
from django.conf.urls import include, url
from . import views


app_name = 'polaaar'
urlpatterns = [
   
    url(r'^$', views.home, name='home'),
    path('data/', views.polaaar_data, name='polaaar_data'),
 
]
