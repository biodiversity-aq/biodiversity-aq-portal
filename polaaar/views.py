from django.shortcuts import render

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

from polaaar.models import *
from accounts.models import UserProfile

def home(request):
    return render(request, 'polaaar_home.html')




def polaaar_data(request):
    qs_results = ProjectMetadata.objects.annotate(geom=AsGeoJSON(Centroid('geomet')))
    return render(request, 'polaaar_data.html',{'qs_results':qs_results})

def spatial_searching(request):    
    return render(request, 'polaaarsearch/spatial_search.html')

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