
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponsePermanentRedirect, HttpResponse
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
    return render(request, 'polaaar_home.html')




def polaaar_data(request):
    qs_results = ProjectMetadata.objects.annotate(geom=AsGeoJSON(Centroid('geomet')))
    return render(request, 'polaaar_data.html',{'qs_results':qs_results})

def spatial_searching(request):
    qs_results = ProjectMetadata.objects.annotate(geom=AsGeoJSON(Centroid('geomet')))
    return render(request, 'polaaarsearch/spatial_search.html',{'qs_results':qs_results})

#def sitemap(request):
#    assert isinstance(request, HttpRequest)
#    X = Sitetable.objects.all()
#    X3 = X.values_list('site','lat','lon')
#    X4 = json.dumps(list(X3), cls=DjangoJSONEncoder)

#    data = {'sites':X4}

#    return render(request,'sitemap.html',data)










#########################################################
### Search views
def polaaar_search(request):
    return render(request, 'polaaar_search.html')


def env_search(request):
    qs = Variable.objects.all()       
    qsenv = Environment.objects.all()
    return render(request, 'polaaarsearch/environment.html',{'qs':qs,'qsenv':qsenv})


def env_searched(request):
    qs = Variable.objects.all()
    if request.method=='GET':
        var = request.GET.get('var','')
        
        #qsenv = Environment.objects.filter(env_variable__name = var)        
        qsenv = Event.objects.filter(environment__env_variable__name = var)
                
        return render(request,'polaaarsearch/env_searched.html',{'qs':qs,'qsenv':qsenv})



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
'''



class sampling_methodSerializer(serializers.ModelSerializer):
	class Meta:
		model = sampling_method
		fields =[
		'url',
		'shortname',
		'description'
		]

class unitsSerializer(serializers.ModelSerializer):
	class Meta:
		model = units
		fields =[
		'url',
		'name',
		'html_tag'
		]
    

class VariableSerializer(serializers.ModelSerializer):
	var_units = serializers.StringRelatedField(many=True)
	method = serializers.StringRelatedField(many=True)
	class Meta:
		model = Variable
		fields =[
		'url',
		'name',
		'var_units',
		'method',
		'var_type'
		]


class EnvironmentSerializer(serializers.ModelSerializer):
	env_variable = VariableSerializer(many=False,read_only=True)
	sequences = SequencesSerializer(many=True,read_only=True)
	
	class Meta:
		model = Environment
		fields =[
		'url',
	    'env_sample_name',
		'created_at',
		'link_climate_info',
		'env_variable',
		'sequences',
		'env_numeric_value',
		'env_text_value'
		]




#########################################################################################################



class EventTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = EventType
		fields = [
		'url',
		'name']



class SampleMetadataSerializer(serializers.ModelSerializer): 
	metadata_creator = serializers.StringRelatedField(many=False)
	geographic_location = GeogSerializer(many=False,read_only=True)
	env_package = PackageSerializer(many=False,read_only=True)
	sequence = SequencesSerializer(many=True,read_only=True)

	class Meta:
		model = SampleMetadata
		fields = [
		'metadata_tag',
		'md_created_on',
		'metadata_creator',        # User FK
		'license',
		'geographic_location',  #FK geog_loc
		'locality',
		'geo_loc_name',
		'env_biome',
		'env_package',   #FK Package
		'env_feature',
		'env_material',
		'institutionID',
		'nucl_acid_amp',
		'nucl_acid_ext',
		'ref_biomaterial',
		'rel_to_oxygen',
		'rightsHolder',
		'samp_collect_device',
		'samp_store_dur',
		'samp_store_loc',
		'samp_store_temp',
		'samp_vol_we_dna_ext',
		'samplingProtocol',
		'source_mat_id',
		'submitted_to_insdc',
		'investigation_type',
		'isol_growth_condt',
		'lib_size',
		'sequence', #M2M  sequences
		'additional_information'
	]




##################### has a router = 'project_metadata'
class ProjectMetadataSerializer(serializers.ModelSerializer):

	associated_references = ReferenceSerializer(many=True,read_only=True)
	#associated_references = serializers.StringRelatedField(many=False)
	project_creator = serializers.StringRelatedField(many=False)
	class Meta:
		model = ProjectMetadata
		fields = [
		'url',
		'project_name',
		'start_date',
		'end_date',
		'EML_URL',
		'abstract',
		'geomet',
		'is_public',
		'associated_references',
		'associated_media',
		'created_on',
		'updated_on',
		'project_creator',
		'project_qaqc'
		]


class EventHierarchySerializer(serializers.ModelSerializer):	
	project_metadata = ProjectMetadataSerializer(many=False,read_only=True)
	event_type = serializers.StringRelatedField(many=False)
	parent_event = serializers.StringRelatedField(many=False)
	event_creator = serializers.StringRelatedField(many=False)
	class Meta:
		model = EventHierarchy
		fields = [
		'url',
		'parent_event_name',
		'event_type',
		'description',
		'parent_event',
		'event_creator',
		'created_on',
		'updated_on',
		'project_metadata']



class TaxaSerializer(serializers.ModelSerializer):
	parent_taxa = serializers.StringRelatedField(many=False)
	class Meta:
		model = Taxa
		fields = [
		'name',
		'TaxonRank',
		'taxonID',
		'parent_taxa'		    
		]



'''














