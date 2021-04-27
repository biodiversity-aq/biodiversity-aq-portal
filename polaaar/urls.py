from __future__ import unicode_literals

from django.urls import path
from django.conf.urls import include, url
from . import views

from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="POLA3R API",
        default_version='v1',
        description="API endpoints of Polar 'Omics Links to Antarctic, Arctic and Alpine Research (POLA3R)",
        license=openapi.License(name="CC BY 4.0", url="https://creativecommons.org/licenses/by/4.0/"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'occurrence', views.OccurrenceViewSet, basename='occurrence')
router.register(r'events', views.EventViewSet, basename='events')
router.register(r'eventhierarchy', views.EventHierarchyViewSet, basename='eventhierarchy')
router.register(r'project_metadata', views.ProjectMetadataViewSet, basename='projectmetadata')
router.register(r'reference', views.ReferenceViewSet, basename='reference')
router.register(r'geog_location', views.GeogViewSet, basename='geoglocation')

### Special routers for sequences and environments
router.register(r'sequence', views.SequencesViewSet, basename='sequences')
router.register(r'environment', views.EnvironmentVariablesViewSet, basename='environmentalvariables')

app_name = 'polaaar'
urlpatterns = [

    url(r'^$', views.home, name='home'),
    path('submit/', views.polaaar_submit, name='polaaar_submit_data'),

    ### Path controls for API routers
    # path('environment/',views.EnvironmentViewSet,name='environment'),
    # path('events/',views.EventViewSet,name='events'),

    path('api_reference/', views.api_reference, name='api_reference'),
    path('environment/', views.EnvironmentListView.as_view(), name='env_search'),
    path('sequence/', views.SequenceListView.as_view(), name='seq_search'),
    path('spatial/', views.SpatialSearchListView.as_view(), name='spatialsearch'),

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
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    ## Swagger urls
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
