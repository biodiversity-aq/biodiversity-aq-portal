from __future__ import unicode_literals
from django.urls import path
from django.conf.urls import include, url
from . import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'occurrence',views.OccurrenceViewSet)
router.register(r'events',views.EventViewSet)
router.register(r'eventhierarchy',views.EventHierarchyViewSet)
router.register(r'project_metadata',views.ProjectMetadataViewSet,basename='projectmetadata')
router.register(r'sequence',views.SequenceViewSet)
router.register(r'reference',views.ReferenceViewSet)
router.register(r'geog_location',views.GeogViewSet)
router.register(r'environment',views.EnvironmentViewSet)

### Special routers for sequences and environments
router.register(r'sequences',views.SequencesViewSet)
router.register(r'environmental_variables',views.EnvironmentVariablesViewSet)

app_name = 'polaaar'
urlpatterns = [
   
    url(r'^$', views.home, name='home'),    
    path('search/',views.polaaar_search,name='polaaar_search'),
    path('submit/',views.polaaar_submit,name='polaaar_submit_data'),

    path('envsearch/',views.env_search,name='env_search'),
    url(r'var/',views.env_searched,name='env_searched'),    
    path('seqsearch/',views.seq_search,name='seq_search'),
    path('spatialsearch/',views.spatial_searching,name='spatialsearch'),
    

    path('submit_data/',views.email_submission,name='email_submission'),
    path('submit_success/',views.submit_success,name='submit_success'),    

    ###  EXCEL export views
    url(r'^export_projects/',views.export_projects,name='export_projects'),
    url(r'^export_environment/',views.export_environment,name='export_environment'),
    url(r'^export_sequences/',views.export_sequences,name='export_sequences'),
    url(r'^export_events/',views.export_events,name='export_events'),

    #### REST API URLS    

    path('',include(router.urls)),
    path('api-auth/',include('rest_framework.urls',namespace='rest_framework'))
 
]
