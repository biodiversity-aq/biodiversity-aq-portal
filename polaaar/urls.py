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
    path('mimsearch/',views.mim_search,name='mim_search'),
    path('seqsearch/',views.seq_search,name='seq_search'),
    path('spasearch/',views.spatial_search,name='spa_search')

 
]
