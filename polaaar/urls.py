from __future__ import unicode_literals

from django.conf.urls import include, url
from . import views


app_name = 'polaaar'
urlpatterns = [
   
    url(r'^$', views.home, name='home'),
 
]
