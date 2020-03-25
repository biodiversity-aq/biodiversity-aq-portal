
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponsePermanentRedirect, HttpResponse, JsonResponse
from django.db.models import Prefetch
from django.contrib.gis.db.models.functions import AsGeoJSON, Centroid 
from django.core.files.storage import FileSystemStorage
from .forms import EmailForm
from django.core.mail import send_mail, EmailMessage
from django.core.serializers import serialize
from django_filters.rest_framework import DjangoFilterBackend

from polaaar.models import *
from accounts.models import UserProfile


from rest_framework import viewsets, filters
from rest_framework import permissions
from polaaar.serializers import *




def home(request):
    qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT')))
    return render(request, 'polaaar_home.html',{'qs_results':qs_results})



def spatial_searching(request):
    qs_results = ProjectMetadata.objects.annotate(geom=AsGeoJSON(Centroid('geomet')))
    return render(request, 'polaaarsearch/spatial_search.html',{'qs_results':qs_results})






########## WRITE A SAVE METHOD THAT INCLUDES A LAT/LON CENTROID! 

#########################################################
### Search views
def polaaar_search(request):	
	qs = ProjectMetadata.objects.prefetch_related('event_hierarchy').all()
	qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT')))
	return render(request, 'polaaar_search.html',{'qs_results':qs_results,'qs':qs})

'''
def p_s_data(request):
	if request.method=="GET":
		idlist = request.GET.get('ids')
		IDs = idlist.split(",")		
		qs_results = Event.objects.filter(event_hierarchy__project_metadata__id__in = IDs).annotate(geom=AsGeoJSON(Centroid('footprintWKT')))		
		return HttpResponse(qs_results,content_type='application/json')
'''



def env_search(request):
    qs = Variable.objects.all()       
    qsenv = Environment.objects.all()
    return render(request, 'polaaarsearch/environment.html',{'qs':qs,'qsenv':qsenv})


def env_searched(request):
	
	if request.method=='GET':
		var = request.GET.get('var','')
		vartype = request.GET.get('vartype','')		
		qsenv = Event.objects.filter(environment__env_variable__name = var)
                
		return render(request,'polaaarsearch/env_searched.html',{'qsenv':qsenv,'vartype':vartype})



def proj_search(request):
    qs = ProjectMetadata.objects.all()
    return render(request, 'polaaarsearch/projects.html',{'qs':qs})


def mim_search(request):
    return render(request, 'polaaarsearch/mimarks.html')

def seq_search(request):

    qs = Sequences.objects.all()

    return render(request, 'polaaarsearch/sequences.html',{'qs':qs})




#########################################################
### Submit views
def polaaar_submit(request):
    return render(request, 'polaaar_submit.html')


def dc_submit(request):
    return render(request, 'polaaarsubmit/submit_dc.html')

def mim_submit(request):
    return render(request, 'polaaarsubmit/submit_mim.html')


#######################################################
##### 
### Email submission views

def email_submission(request):

    usr = request.user
    if usr.is_authenticated:
        init = {'email':usr.email}
    else:
        init = {'email':''}
    if request.method == "POST":
       
        form = EmailForm(request.POST,request.FILES,initial=init)
        if form.is_valid():
            post = form.save(commit=False)
            #post.published_date = timezone.now()
            post.save()
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            document = request.FILES.get('document')
            email_from = settings.SENDER_MAIL
            recipient_list = ['humphries.grant@gmail.com']
            email = EmailMessage(subject,message,email_from,recipient_list)
            base_dir = 'media/uploads/'
            email.attach_file('media/uploads/'+str(document))
            email.send()
            response = redirect('/polaaar/submit_success/')
            return response
    else:
        form = EmailForm(initial=init)
    return render(request, 'polaaarsubmit/email_submission.html', {'form': form})


def submit_success(request):
    return render(request, 'polaaarsubmit/submit_success.html')




###################################################################################################################

#### REST API views

class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['full_reference','year']

class SequencesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sequences.objects.all()
    serializer_class = SequencesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
    'sequence_name':['exact','icontains'],
	'target_gene':['exact','icontains'],
	'primerName_forward':['exact','icontains'],
	'primerName_reverse':['exact','icontains'],
	'seqData_numberOfBases':['gte','lte','exact'],
	'seqData_numberOfSequences':['gte','lte','exact'],    
	}


class ProjectMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectMetadata.objects.all()
    serializer_class = ProjectMetadataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
    'id':['in'],
    'project_name':['exact','icontains'],
	'start_date':['exact','icontains','gte','lte'],
	'end_date':['exact','icontains','gte','lte'],    
	'abstract':['icontains'],
	'is_public':['exact'],
	## Creator search
	'project_creator__full_name':['exact','icontains'],
	## Reference search
	'associated_references__full_reference':['icontains'],
	## Event hierarchy search
	'event_hierarchy__event_hierarchy_name':['exact','icontains'],
	'event_hierarchy__description':['icontains'],
	'event_hierarchy__event_type__name':['icontains'],
	## Event search
	'event_hierarchy__event__parent_event__sample_name':['icontains'],							# This references the __str__ argument from the model (back to 'self')
	'event_hierarchy__event__sample_name':['icontains'],
	## Sequence search
	'event_hierarchy__event__event_metadata__sequence__sequence_name':['exact','icontains'],
	'event_hierarchy__event__event_metadata__sequence__target_gene':['exact','icontains'],
	'event_hierarchy__event__event_metadata__sequence__primerName_forward':['exact','icontains'],
	'event_hierarchy__event__event_metadata__sequence__primerName_reverse':['exact','icontains'],
	'event_hierarchy__event__event_metadata__sequence__seqData_numberOfBases':['gte','lte','exact'],
	'event_hierarchy__event__event_metadata__sequence__seqData_numberOfSequences':['gte','lte','exact'],    
	}



class EventHierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventHierarchy.objects.all()
    serializer_class = EventHierarchySerializer
    filter_backends = [DjangoFilterBackend]        
    filterset_fields = {    
     'event_hierarchy_name':['exact','istartswith','icontains'],
     'description':['icontains'],
	}

class OccurrenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer
    filter_backends = [DjangoFilterBackend]        
    filterset_fields = {    
     'occurrenceID':['exact','istartswith','icontains']
	}

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
    #'collection_date':['gte','lte'],
     'sample_name':['exact','istartswith'],
	 'id':['exact','in']
     #'parent_event__project_metadata__project_name':['exact','icontains']
	}

class GeogViewSet(viewsets.ReadOnlyModelViewSet):	
	queryset = Geog_Location.objects.all()
	serializer_class = GeogSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = {
		'name':['exact']
	}
	

class EnvironmentViewSet(viewsets.ReadOnlyModelViewSet):	
	queryset = Environment.objects.all()
	serializer_class = EnvironmentSerializer
	filter_backends = [DjangoFilterBackend]
	


###########################################################################














