from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponsePermanentRedirect
from django.db.models import Prefetch
from django.contrib.gis.db.models.functions import AsGeoJSON, Centroid 


from polaaar.models import *


def home(request):
    return render(request, 'polaaar_home.html')


def polaaar_data(request):

    #qs_results = ProjectMetadata.objects.annotate(geom=AsGeoJSON(Centroid('geomet')))


    return render(request, 'polaaar_data.html')#,{'qs_results':qs_results})

#########################################################
### Search views
def polaaar_search(request):
    return render(request, 'polaaar_search.html')


def env_search(request):
    return render(request, 'polaaarsearch/environment.html')

def proj_search(request):
    qs = ProjectMetadata.objects.all()
    return render(request, 'polaaarsearch/projects.html',{'qs':qs})


def mim_search(request):
    return render(request, 'polaaarsearch/mimarks.html')

def seq_search(request):
    return render(request, 'polaaarsearch/sequences.html')

def spatial_search(request):
    return render(request, 'polaaarsearch/spatial.html')



#########################################################
### Submit views
def polaaar_submit(request):
    return render(request, 'polaaar_submit.html')


def dc_submit(request):
    return render(request, 'polaaarsubmit/submit_dc.html')

def mim_submit(request):
    return render(request, 'polaaarsubmit/submit_mim.html')


#########################################################