from __future__ import unicode_literals
from django.urls import path
from django.conf.urls import include, url
from . import views


app_name = 'polaaar'
urlpatterns = [
   
    url(r'^$', views.home, name='home'),
    path('data/', views.polaaar_data, name='polaaar_data'),
    path('search/',views.polaaar_search,name='polaaar_search'),
    path('submit/',views.polaaar_submit,name='polaaar_submit_data'),

    path('envsearch/',views.env_search,name='env_search'),
    url(r'var/',views.env_searched,name='env_searched'),
    path('mimsearch/',views.mim_search,name='mim_search'),
    path('seqsearch/',views.seq_search,name='seq_search'),
    path('spasearch/',views.spatial_search,name='spa_search'),
    path('projsearch/',views.proj_search,name='proj_search'),

    path('submit_data/',views.email_submission,name='email_submission'),
    path('submit_success/',views.submit_success,name='submit_success'),
    path('dcsubmit/',views.dc_submit,name='dc_submit'),
    path('mimsubmit/',views.mim_submit,name='mim_submit'),


    path('spatialsearch/',views.spatial_searching,name='spatialsearch'),

 
]
