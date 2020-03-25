from __future__ import unicode_literals
from django.urls import path
from django.conf.urls import include, url
from . import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'occurrence',views.OccurrenceViewSet)
router.register(r'events',views.EventViewSet)
router.register(r'eventhierarchy',views.EventHierarchyViewSet)
router.register(r'project_metadata',views.ProjectMetadataViewSet)
router.register(r'sequences',views.SequencesViewSet)
router.register(r'reference',views.ReferenceViewSet)
router.register(r'geog_location',views.GeogViewSet)
router.register(r'environment',views.EnvironmentViewSet)



app_name = 'polaaar'
urlpatterns = [
   
    url(r'^$', views.home, name='home'),    
    path('search/',views.polaaar_search,name='polaaar_search'),
    path('submit/',views.polaaar_submit,name='polaaar_submit_data'),

    path('envsearch/',views.env_search,name='env_search'),
    url(r'var/',views.env_searched,name='env_searched'),
    path('mimsearch/',views.mim_search,name='mim_search'),
    path('seqsearch/',views.seq_search,name='seq_search'),
    path('spatialsearch/',views.spatial_searching,name='spatialsearch'),
    #path('projsearch/',views.proj_search,name='proj_search'),

    path('submit_data/',views.email_submission,name='email_submission'),
    path('submit_success/',views.submit_success,name='submit_success'),
    path('dcsubmit/',views.dc_submit,name='dc_submit'),
    path('mimsubmit/',views.mim_submit,name='mim_submit'),

    #### REST API URLS

    path('',include(router.urls)),
    path('api-auth/',include('rest_framework.urls',namespace='rest_framework'))
    

 
]
