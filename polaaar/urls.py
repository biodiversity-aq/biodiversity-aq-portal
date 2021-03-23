from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import include, url
from . import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'occurrence', views.OccurrenceViewSet, basename='occurrence')
router.register(r'events', views.EventViewSet, basename='events')
router.register(r'eventhierarchy', views.EventHierarchyViewSet, basename='eventhierarchy')
router.register(r'project_metadata', views.ProjectMetadataViewSet, basename='projectmetadata')
router.register(r'sequence', views.SequenceViewSet, basename='sequence')
router.register(r'reference', views.ReferenceViewSet, basename='reference')
router.register(r'geog_location', views.GeogViewSet, basename='geoglocation')
router.register(r'environment', views.EnvironmentViewSet, basename='environment')

### Special routers for sequences and environments
router.register(r'sequences', views.SequencesViewSet, basename='sequences')
router.register(r'environmental_variables', views.EnvironmentVariablesViewSet, basename='environmentalvariables')

app_name = 'polaaar'
urlpatterns = [

    url(r'^$', views.home, name='home'),
    path('search/', views.polaaar_search, name='polaaar_search'),
    path('submit/', views.polaaar_submit, name='polaaar_submit_data'),

    ### Path controls for API routers
    # path('environment/',views.EnvironmentViewSet,name='environment'),
    # path('events/',views.EventViewSet,name='events'),

    path('api_reference/', views.api_reference, name='api_reference'),
    path('environment/', views.env_search, name='env_search'),
    path('seqsearch/', views.seq_search, name='seq_search'),
    path('spatialsearch/', views.spatial_searching, name='spatialsearch'),
    path('spatial_search_table/', views.spatial_search_table, name='spatial_search_table'),

    path('project/', views.ProjectMetadataListView.as_view(), name='project_metadata_list'),
    path('project/<int:pk>/', views.project_metadata_detail, name='project_metadata_detail'),

    path('submit_data/', views.email_submission, name='email_submission'),
    path('submit_success/', views.submit_success, name='submit_success'),

    ###  EXCEL export views
    url(r'^export_projects/', views.export_projects, name='export_projects'),
    url(r'^export_environment/', views.export_environment, name='export_environment'),
    url(r'^export_sequences/', views.export_sequences, name='export_sequences'),
    url(r'^export_events/', views.export_events, name='export_events'),

    ###  View to export raw data files
    path('export_raw_data/<int:pk>', views.GetProjectFiles, name='GetProjectFiles'),

    #### REST API URLS    
    url(r'^api_reference/', views.api_reference, name='api_reference'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]
