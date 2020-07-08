from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.gis.db.models.functions import AsGeoJSON, Centroid
from .forms import EmailForm
from django.core.mail import EmailMessage
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from biodiversity.decorators import verify_recaptcha
from polaaar.serializers import *
from polaaar.models import Reference

import xlsxwriter
import io
import datetime
import zipfile
import os


def home(request):
    qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT')))
    return render(request, 'polaaar/polaaar_home.html', {'qs_results': qs_results})


#########################################################
### DJANGO Search views
##########  

def polaaar_search(request):
    user = request.user

    #### This is used to generate the links back to the project search page. If there is a ?pid search string 
    #### Then the user is directed to the project search page with data filtered by that specific project.

    if len(request.GET.get('pid', '')):
        proj = request.GET.get('pid', '')

        if user.is_authenticated and user.is_superuser:
            qs = ProjectMetadata.objects.filter(id=proj)

            qs_results = Event.objects.annotate(
                geom=AsGeoJSON(Centroid('footprintWKT'))).filter(id=proj)

        elif user.is_authenticated:
            qs = ProjectMetadata.objects.filter(Q(is_public=True) | Q(
                project_creator__username=user.username)).filter(id=proj).prefetch_related('event_hierarchy')

            qs_results = Event.objects.annotate(
                geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            qs = ProjectMetadata.objects.filter(Q(is_public=True)).filter(id=proj).prefetch_related('event_hierarchy')

            qs_results = Event.objects.annotate(
                geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
                Q(event_hierarchy__project_metadata__is_public=True))
        buttondisplay = "Display events"
        ## This triggers a refresh button to appear in the project search tool if the user is looking at filtered project data
        viewprojs = True

    else:

        if user.is_authenticated and user.is_superuser:
            qs = ProjectMetadata.objects.all()
            qs_results = Event.objects.annotate(
                geom=AsGeoJSON(Centroid('footprintWKT'))).all()
        elif user.is_authenticated:
            qs = ProjectMetadata.objects.filter(Q(is_public=True) | Q(
                project_creator__username=user.username)).prefetch_related('event_hierarchy')
            qs_results = Event.objects.annotate(
                geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            qs = ProjectMetadata.objects.filter(Q(is_public=True)).prefetch_related('event_hierarchy')
            qs_results = Event.objects.annotate(
                geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
                Q(event_hierarchy__project_metadata__is_public=True))
        buttondisplay = "Refresh map"
        viewprojs = False
    return render(request, 'polaaar/polaaar_search.html',
                  {'qs_results': qs_results, 'qs': qs, 'buttondisplay': buttondisplay, 'viewprojs': viewprojs})


def env_search(request):
    qs = Variable.objects.all()
    return render(request, 'polaaar/polaaarsearch/environment.html', {'qs': qs})


def env_searched(request):
    user = request.user
    if request.method == 'GET':
        var = request.GET.get('var', '')
        vars = var.split(',')

        # vartype = request.GET.get('vartype','')
        if user.is_authenticated and user.is_superuser:

            qsenv = Environment.objects.filter(env_variable__name__in=vars)

        elif user.is_authenticated:

            qsenv = Environment.objects.filter(env_variable__name__in=vars).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

        else:

            qsenv = Environment.objects.filter(env_variable__name__in=vars).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

        Y = qsenv.values_list('env_variable__var_type')

        try:
            x = list(Y).index(('NUM',))
            x = True
        except:
            x = False

        return render(request, 'polaaar/polaaarsearch/env_searched.html', {'qsenv': qsenv, 'test': x})  # ,'vartype':vartype


def seq_search(request):
    user = request.user
    if user.is_authenticated and user.is_superuser:
        qs = Sequences.objects.all().select_related()
    elif user.is_authenticated:
        qs = Sequences.objects.filter(
            Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                event__event_hierarchy__project_metadata__project_creator__username=user.username)).select_related()
    else:
        qs = Sequences.objects.filter(
            Q(event__event_hierarchy__project_metadata__is_public=True)).select_related()
    return render(request, 'polaaar/polaaarsearch/sequences.html', {'qs': qs})


def spatial_searching(request):
    user = request.user
    if user.is_authenticated and user.is_superuser:
        qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT'))).all().select_related()
    if user.is_authenticated:
        qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
            Q(event_hierarchy__project_metadata__is_public=True) | Q(
                event_hierarchy__project_metadata__project_creator__username=user.username))
    else:
        qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
            Q(event_hierarchy__project_metadata__is_public=True))
    return render(request, 'polaaar/polaaarsearch/spatial_search.html', {'qs_results': qs_results})


def spatial_search_table(request):
    user = request.user
    if request.method == "GET":
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')
        if user.is_authenticated and user.is_superuser:
            qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
                pk__in=IDS).select_related()
        if user.is_authenticated:
            qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username)).filter(pk__in=IDS)
        else:
            qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
                Q(event_hierarchy__project_metadata__is_public=True)).filter(pk__in=IDS)

    return render(request, 'polaaar/polaaarsearch/spatial_search_table.html', {'qs_results': qs_results})


#########################################################
### Download project files

def GetProjectFiles(request, pk):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    if request.method == "GET":
        pf = ProjectFiles.objects.filter(project__id=pk)
        filenames = [x.files.path for x in pf]
        pfnm = ProjectMetadata.objects.filter(id=pk).values_list('project_name')[0][0]
        pfnm = '-'.join(pfnm.split(' '))  # remove spaces in file name

        # Folder name in ZIP archive which contains the above files
        # E.g [thearchive.zip]/somefiles/file2.txt
        zip_subdir = "%s_raw-files" % pfnm
        zip_filename = "%s.zip" % zip_subdir

        # Open StringIO to grab in-memory ZIP contents
        s = io.BytesIO()

        # The zip compressor
        zf = zipfile.ZipFile(s, "w")

        for fpath in filenames:
            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)

            # Add file, at correct path
            zf.write(fpath, zip_path)

        # Must close zip for all contents to be written
        zf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        # ..and correct content-disposition
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

        return resp


#########################################################
### Submit views
def polaaar_submit(request):
    return render(request, 'polaaar/polaaar_submit.html')


#######################################################
##### 
### Email submission views
@verify_recaptcha
def email_submission(request):
    usr = request.user
    if usr.is_authenticated:
        init = {'email': usr.email}
    else:
        init = {'email': ''}
    form = EmailForm(request.POST, request.FILES, initial=init)
    if request.method == "POST":
        if form.is_valid() and request.recaptcha_is_valid:
            post = form.save(commit=False)
            post.save()
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')
            document = form.cleaned_data.get('document')
            email_from = settings.SENDER_MAIL
            recipient_list = settings.POLAAAR_ADMIN_LIST
            email = EmailMessage(subject, message, email_from, recipient_list)
            if document:
                file = os.path.join(settings.MEDIA_ROOT, settings.POLAAAR_MAIL_FILE_DIR, document.name)
                email.attach_file(file)
            email.send()
            submit_success_url = reverse('polaaar:submit_success')
            response = redirect(submit_success_url)
            return response
    return render(request, 'polaaar/polaaarsubmit/email_submission.html',
                  # site key is needed to be rendered in the template
                  {'form': form, 'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY})


def submit_success(request):
    return render(request, 'polaaar/polaaarsubmit/submit_success.html')


###################################################################################################################
#### REST API views
#### These views are instantiated with viewsets to keep the query calls simple and avoid us having to write custom CRUD calls. 

class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReferenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['full_reference', 'year']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Reference.objects.all()
        elif user.is_authenticated:
            queryset = Reference.objects.filter(
                Q(associated_projects__project_metadata__is_public=True) | Q(
                    associated_projects__project_metadata__project_creator__username=user.username)).order_by(
                'full_reference').distinct('full_reference')
        else:
            queryset = Reference.objects.filter(Q(
                associated_projects__project_metadata__is_public=True)).order_by('full_reference').distinct(
                'full_reference')
        return queryset


class SequenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SequencesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'sequence_name': ['exact', 'icontains'],
        'target_gene': ['exact', 'icontains'],
        'primerName_forward': ['exact', 'icontains'],
        'primerName_reverse': ['exact', 'icontains'],
        'seqData_numberOfBases': ['gte', 'lte', 'exact'],
        'seqData_numberOfSequences': ['gte', 'lte', 'exact'],
        'id': ['in']
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Sequences.objects.all()
        elif user.is_authenticated:
            queryset = Sequences.objects.filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            queryset = Sequences.objects.filter(Q(event__event_hierarchy__project_metadata__is_public=True))
        return queryset


class ProjectMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectMetadataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'id': ['in'],
        'project_name': ['exact', 'icontains'],
        'start_date': ['exact', 'icontains', 'gte', 'lte'],
        'end_date': ['exact', 'icontains', 'gte', 'lte'],
        'abstract': ['icontains'],
        'is_public': ['exact'],
        ## Creator search
        'project_creator__full_name': ['exact', 'icontains'],
        ## Reference search
        'associated_references__full_reference': ['icontains'],

        ## Event hierarchy search
        'event_hierarchy__event_hierarchy_name': ['exact', 'icontains'],
        'event_hierarchy__description': ['icontains'],
        'event_hierarchy__event_type__name': ['icontains'],
        ### Event search
        'event_hierarchy__event__parent_event__sample_name': ['icontains'],
        # This references the __str__ argument from the model (back to 'self')
        'event_hierarchy__event__sample_name': ['icontains'],
        ### Sequence search
        'event_hierarchy__event__sequences__sequence_name': ['exact', 'icontains'],
        'event_hierarchy__event__sequences__target_gene': ['exact', 'icontains'],
        'event_hierarchy__event__sequences__primerName_forward': ['exact', 'icontains'],
        'event_hierarchy__event__sequences__primerName_reverse': ['exact', 'icontains'],
        'event_hierarchy__event__sequences__seqData_numberOfBases': ['gte', 'lte', 'exact'],
        'event_hierarchy__event__sequences__seqData_numberOfSequences': ['gte', 'lte', 'exact'],

    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = ProjectMetadata.objects.all().prefetch_related('event_hierarchy')
        elif user.is_authenticated:
            queryset = ProjectMetadata.objects.filter(Q(is_public=True) | Q(
                project_creator__username=user.username)).prefetch_related('event_hierarchy')
        else:
            queryset = ProjectMetadata.objects.filter(Q(is_public=True)).prefetch_related('event_hierarchy')
        return queryset


class EventHierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventHierarchySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'event_hierarchy_name': ['exact', 'istartswith', 'icontains'],
        'description': ['icontains'],
        'id': ['in']
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = EventHierarchy.objects.all()
        elif user.is_authenticated:
            queryset = EventHierarchy.objects.filter(
                Q(project_metadata__is_public=True) | Q(project_metadata__project_creator__username=user.username))
        else:
            queryset = EventHierarchy.objects.filter(Q(project_metadata__is_public=True))
        return queryset


class OccurrenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OccurrenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'occurrenceID': ['exact', 'istartswith', 'icontains']
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Occurrence.objects.all()
        elif user.is_authenticated:
            queryset = Occurrence.objects.filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            queryset = Occurrence.objects.filter(Q(event__event_hierarchy__project_metadata__is_public=True))
        return queryset


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'collection_year': ['gte', 'lte', 'exact', 'in'],
        'sample_name': ['exact', 'istartswith'],
        'id': ['exact', 'in']
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Event.objects.all()
        elif user.is_authenticated:
            queryset = Event.objects.filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            queryset = Event.objects.filter(Q(event_hierarchy__project_metadata__is_public=True))
        return queryset


class GeogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GeogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'name': ['exact']
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Geog_Location.objects.all()
        elif user.is_authenticated:
            queryset = Geog_Location.objects.filter(
                Q(sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__is_public=True) | Q(
                    sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__project_creator__username=user.username)).order_by(
                'name').distinct('name')
        else:
            queryset = Geog_Location.objects.filter(Q(
                sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__is_public=True)).order_by(
                'name').distinct('name')
        return queryset


class EnvironmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Environment.objects.all()
        elif user.is_authenticated:
            queryset = Environment.objects.filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            queryset = Environment.objects.filter(Q(event__event_hierarchy__project_metadata__is_public=True))
        return queryset


###########################################################################

### Special views for the sequence download


class SequencesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SequencesSerializer2
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'sequence_name': ['exact', 'icontains'],
        'target_gene': ['exact', 'icontains'],
        'primerName_forward': ['exact', 'icontains'],
        'primerName_reverse': ['exact', 'icontains'],
        'seqData_numberOfBases': ['gte', 'lte', 'exact'],
        'seqData_numberOfSequences': ['gte', 'lte', 'exact'],
        'id': ['in']
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Sequences.objects.all()
        elif user.is_authenticated:
            queryset = Sequences.objects.filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            queryset = Sequences.objects.filter(Q(event__event_hierarchy__project_metadata__is_public=True))
        return queryset


### Special view for the Environment download

class EnvironmentVariablesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentSerializer2
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'env_sample_name': ['icontains'],
        'env_variable__name': ['exact', 'icontains', 'in'],
        'env_method__shortname': ['exact', 'icontains'],
        'env_text_value': ['exact', 'in', 'icontains'],
        'env_numeric_value': ['gte', 'lte'],
        'event__sample_name': ['exact', 'icontains'],
        'event__event_hierarchy__project_metadata__project_name': ['exact', 'icontains'],
        'id': ['in']
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            queryset = Environment.objects.all()
        elif user.is_authenticated:
            queryset = Environment.objects.filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))
        else:
            queryset = Environment.objects.filter(Q(event__event_hierarchy__project_metadata__is_public=True))
        return queryset


###################################################################################################################################################################################
### Project level XLSX download
### This creates an XLSX sheet with multiple worksheets 

#########################################################################################################################################
####### THESE ARE ALL 'GET' CALLS RIGHT NOW, BUT MAY NEED TO SWITCH TO POST CALLS IF THE NUMBER OF EVENTS IS TOO HIGH #####################
#########################################################################################################################################

def export_projects(request):
    user = request.user
    if request.method == 'GET':
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')

        ###########################################################
        ## Authentication checks and queries
        if user.is_authenticated and user.is_superuser:

            PM = ProjectMetadata.objects.filter(id__in=IDS)

            EH = EventHierarchy.objects.filter(project_metadata__id__in=IDS)

            E = Event.objects.filter(event_hierarchy__project_metadata__id__in=IDS)

            S = Sequences.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS)

            O = Occurrence.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS)

            Env = Environment.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS)

            G = Geog_Location.objects.filter(
                sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__id__in=IDS)

            R = Reference.objects.filter(associated_projects__id__in=IDS)

            T = Taxa.objects.filter(occurrence__event__event_hierarchy__project_metadata__id__in=IDS)

        elif user.is_authenticated:

            PM = ProjectMetadata.objects.filter(id__in=IDS).filter(
                Q(is_public=True) | Q(project_creator__username=user.username))

            EH = EventHierarchy.objects.filter(project_metadata__id__in=IDS).filter(
                Q(project_metadata__is_public=True) | Q(project_metadata__project_creator__username=user.username))

            E = Event.objects.filter(event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username))

            S = Sequences.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

            O = Occurrence.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

            Env = Environment.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

            G = Geog_Location.objects.filter(
                sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__is_public=True) | Q(
                    sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__project_creator__username=user.username))

            R = Reference.objects.filter(associated_projects__id__in=IDS).filter(
                Q(associated_projects__is_public=True) | Q(
                    associated_projects__project_creator__username=user.username))

            T = Taxa.objects.filter(occurrence__event__event_hierarchy__project_metadata__id__in=IDS).filter(Q(
                occurrence__event__event_hierarchy__project_metadata__is_public=True) | Q(
                occurrence__event__event_hierarchy__project_metadata__project_creator__username=user.username))
        else:

            PM = ProjectMetadata.objects.filter(id__in=IDS).filter(Q(is_public=True))

            EH = EventHierarchy.objects.filter(project_metadata__id__in=IDS).filter(Q(project_metadata__is_public=True))

            E = Event.objects.filter(event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event_hierarchy__project_metadata__is_public=True))

            S = Sequences.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

            O = Occurrence.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

            Env = Environment.objects.filter(event__event_hierarchy__project_metadata__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

            G = Geog_Location.objects.filter(
                sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__id__in=IDS).filter(Q(
                sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__is_public=True))

            R = Reference.objects.filter(associated_projects__id__in=IDS).filter(Q(associated_projects__is_public=True))

            T = Taxa.objects.filter(occurrence__event__event_hierarchy__project_metadata__id__in=IDS).filter(Q(
                occurrence__event__event_hierarchy__project_metadata__is_public=True))
        ##########################################################

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        projectsheet = workbook.add_worksheet("Project metadata")
        eventHsheet = workbook.add_worksheet("Event Hierarchy")
        eventsheet = workbook.add_worksheet("Events")
        sequencesheet = workbook.add_worksheet("Sequences")
        occursheet = workbook.add_worksheet("Occurrences")
        envirsheet = workbook.add_worksheet("Environmental")
        geomsheet = workbook.add_worksheet("Geography")
        refsheet = workbook.add_worksheet("References")
        taxasheet = workbook.add_worksheet("Taxa")
        tdformat = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        ###########################################################################################################################
        ### Write project metadata sheet
        project_header_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator',
            'project_qaqc'
        ]
        project_query_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator__full_name',
            'project_qaqc'
        ]
        PMlist = PM.annotate(geome=AsGeoJSON('geomet')).values_list(*project_query_row)

        for col_num, data in enumerate(project_header_row):
            projectsheet.write(0, col_num, data)

        for col_num, data in enumerate(PMlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 1 or row_num == 2 or row_num == 7 or row_num == 8):
                    projectsheet.write(col_num, row_num, data2, tdformat)
                else:
                    projectsheet.write(col_num, row_num, data2)

        ###############################################################################
        ### Write event hierarchy sheet
        eventH_header = [
            'event_hierarchy_name',
            'event_type',
            'description',
            'parent_event_hierarchy',
            'created_on',
            'project_name'
        ]
        eventH_query = [
            'event_hierarchy_name',
            'event_type__name',
            'description',
            'parent_event_hierarchy__event_hierarchy_name',
            'created_on',
            'project_metadata__project_name'
        ]
        EHlist = EH.values_list(*eventH_query)
        for col_num, data in enumerate(eventH_header):
            eventHsheet.write(0, col_num, data)

        for col_num, data in enumerate(EHlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 4):
                    eventHsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventHsheet.write(col_num, row_num, data2)

        ################################################################################
        ### Write Event worksheet
        event_header = [
            'project_name',
            'event_hierarchy',
            'sample_name',
            'parent_event',
            'geom',
            'centroid_lat',
            'centroid_lon',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ### Metadata integrated
            'metadata_tag',
            'md_created_on',
            'metadata_creator',
            'license',
            'geographic_location',
            'locality',
            'geo_loc_name',
            'env_biome',
            'env_package',
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
            'source_mat_id',
            'submitted_to_insdc',
            'investigation_type',
            'isol_growth_condt',
            'lib_size',
            'additional_information'
        ]
        event_query = [
            'event_hierarchy__project_metadata__project_name',
            'event_hierarchy__event_hierarchy_name',
            'sample_name',
            'parent_event__sample_name',
            'geom',
            'Latitude',
            'Longitude',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ## Metadata integrated
            'event_metadata__metadata_tag',
            'event_metadata__md_created_on',
            'event_metadata__metadata_creator__full_name',
            'event_metadata__license',
            'event_metadata__geographic_location__name',
            'event_metadata__locality',
            'event_metadata__geo_loc_name',
            'event_metadata__env_biome',
            'event_metadata__env_package__name',
            'event_metadata__env_feature',
            'event_metadata__env_material',
            'event_metadata__institutionID',
            'event_metadata__nucl_acid_amp',
            'event_metadata__nucl_acid_ext',
            'event_metadata__ref_biomaterial',
            'event_metadata__rel_to_oxygen',
            'event_metadata__rightsHolder',
            'event_metadata__samp_collect_device',
            'event_metadata__samp_store_dur',
            'event_metadata__samp_store_loc',
            'event_metadata__samp_store_temp',
            'event_metadata__samp_vol_we_dna_ext',
            'event_metadata__samplingProtocol',
            'event_metadata__source_mat_id',
            'event_metadata__submitted_to_insdc',
            'event_metadata__investigation_type',
            'event_metadata__isol_growth_condt',
            'event_metadata__lib_size',
            'event_metadata__additional_information'
        ]
        Elist = E.annotate(geom=AsGeoJSON('footprintWKT')).values_list(*event_query)
        for col_num, data in enumerate(event_header):
            eventsheet.write(0, col_num, data)

        for col_num, data in enumerate(Elist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 14):
                    eventsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventsheet.write(col_num, row_num, data2)
        ###########################################################################
        ### Sequences worksheet
        sequence_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        sequence_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        Slist = S.values_list(*sequence_query)
        for col_num, data in enumerate(sequence_header):
            sequencesheet.write(0, col_num, data)

        for col_num, data in enumerate(Slist, 1):
            for row_num, data2 in enumerate(data):
                sequencesheet.write(col_num, row_num, data2)
        #############################################################################
        ### Occurrence sheet
        # occursheet
        occur_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'occurrenceID',
            'taxon',
            'occurrence_notes',
            'occurrence_status',
            'occurrence_class',
            'catalog_number',
            'date_identified',
            'other_catalog_numbers',
            'recorded_by'
        ]
        occur_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'occurrenceID',
            'taxon__name',
            'occurrence_notes',
            'occurrence_status',
            'occurrence_class',
            'catalog_number',
            'date_identified',
            'other_catalog_numbers',
            'recorded_by'
        ]
        Olist = O.values_list(*occur_query)
        for col_num, data in enumerate(occur_header):
            occursheet.write(0, col_num, data)

        for col_num, data in enumerate(Olist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 9):
                    occursheet.write(col_num, row_num, data2, tdformat)
                else:
                    occursheet.write(col_num, row_num, data2)
        #######################################################################################
        ### Environmental data worksheet

        envir_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'env_sample_name',
            'link_climate_info',
            'env_variable',
            'env_method',
            'env_units',
            'env_numeric_value',
            'env_text_value'
        ]
        envir_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'env_sample_name',
            'link_climate_info',
            'env_variable__name',
            'env_method__shortname',
            'env_units__name',
            'env_numeric_value',
            'env_text_value'
        ]
        Envlist = Env.values_list(*envir_query)
        for col_num, data in enumerate(envir_header):
            envirsheet.write(0, col_num, data)

        for col_num, data in enumerate(Envlist, 1):
            for row_num, data2 in enumerate(data):
                envirsheet.write(col_num, row_num, data2)
        ########################################################################
        #### Geography worksheet
        geog_header = [
            'name',
            'geog_level',
            'parent_1',
            'parent_2',
            'parent_3',
            'parent_4',
            'parent_5',
            'parent_6',
            'parent_7',
            'parent_8'
        ]
        geog_query = [
            'name',
            'geog_level',
            'parent_geog__name',
            'parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name'
        ]
        Glist = G.values_list(*geog_query)
        for col_num, data in enumerate(geog_header):
            geomsheet.write(0, col_num, data)

        for col_num, data in enumerate(Glist, 1):
            for row_num, data2 in enumerate(data):
                geomsheet.write(col_num, row_num, data2)
        ##############################################################################
        ### References worksheet
        ref_header = [
            'full_reference',
            'doi',
            'year',
            'associated_projects'
        ]
        ref_query = [
            'full_reference',
            'doi',
            'year',
            'associated_projects__project_name'
        ]
        Rlist = R.values_list(*ref_query)
        for col_num, data in enumerate(ref_header):
            refsheet.write(0, col_num, data)

        for col_num, data in enumerate(Rlist, 1):
            for row_num, data2 in enumerate(data):
                refsheet.write(col_num, row_num, data2)
        #####################################################################################
        ### Taxa worksheet
        taxa_header = [
            'name',
            'TaxonRank',
            'taxonID',
            'parent_1',
            'parent_2',
            'parent_3',
            'parent_4',
            'parent_5',
            'parent_6',
            'parent_7',
            'parent_8',
            'parent_9',
            'parent_10',
            'parent_11',
            'parent_12',
            'parent_13',
            'parent_14',
            'parent_15',
            'parent_16'
        ]
        taxa_query = [
            'name',
            'TaxonRank',
            'taxonID',
            'parent_taxa__name',
            'parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name'
        ]
        Tlist = T.values_list(*taxa_query)
        for col_num, data in enumerate(taxa_header):
            taxasheet.write(0, col_num, data)

        for col_num, data in enumerate(Tlist, 1):
            for row_num, data2 in enumerate(data):
                taxasheet.write(col_num, row_num, data2)

        ################################################################################
        workbook.close()
        output.seek(0)
        curdate = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = 'POLA3R_project_metadata_' + curdate + '.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        output.close()
        return (response)


#######################################################################################################################################
#### Returns an excel spreadsheet for the environmental data

def export_environment(request):
    user = request.user
    if request.method == 'GET':
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')

        ###########################################################################################################
        #### Authentication checks

        if user.is_authenticated and user.is_superuser:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__environment__id__in=IDS).distinct(
                'project_name')

            EH = EventHierarchy.objects.filter(event__environment__id__in=IDS).distinct('event_hierarchy_name')

            E = Event.objects.filter(environment__id__in=IDS).order_by('sample_name').distinct('sample_name')

            S = Sequences.objects.filter(event__environment__id__in=IDS).order_by('sequence_name').distinct(
                'sequence_name')

            O = Occurrence.objects.filter(event__environment__id__in=IDS).order_by('occurrenceID').distinct(
                'occurrenceID')

            Env = Environment.objects.filter(id__in=IDS)

        elif user.is_authenticated:

            PM = ProjectMetadata.objects.filter(
                event_hierarchy__event__environment__id__in=IDS).filter(Q(
                is_public=True) | Q(project_creator__username=user.username)).distinct('project_name')

            EH = EventHierarchy.objects.filter(event__environment__id__in=IDS).filter(
                Q(project_metadata__is_public=True) | Q(
                    project_metadata__project_creator__username=user.username)).distinct('event_hierarchy_name')

            E = Event.objects.filter(environment__id__in=IDS).filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username)).order_by(
                'sample_name').distinct('sample_name')

            S = Sequences.objects.filter(event__environment__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username)).order_by(
                'sequence_name').distinct('sequence_name')

            O = Occurrence.objects.filter(event__environment__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username)).order_by(
                'occurrenceID').distinct('occurrenceID')

            Env = Environment.objects.filter(id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

        else:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__environment__id__in=IDS).filter(
                Q(is_public=True)).distinct('project_name')

            EH = EventHierarchy.objects.filter(event__environment__id__in=IDS).filter(
                Q(project_metadata__is_public=True)).distinct('event_hierarchy_name')

            E = Event.objects.filter(environment__id__in=IDS).filter(Q(
                event_hierarchy__project_metadata__is_public=True)).order_by('sample_name').distinct('sample_name')

            S = Sequences.objects.filter(event__environment__id__in=IDS).filter(Q(
                event__event_hierarchy__project_metadata__is_public=True)).order_by('sequence_name').distinct(
                'sequence_name')

            O = Occurrence.objects.filter(event__environment__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True)).order_by('occurrenceID').distinct(
                'occurrenceID')

            Env = Environment.objects.filter(id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))
        ###########################################################################################################

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        projectsheet = workbook.add_worksheet("Project metadata")
        eventHsheet = workbook.add_worksheet("Event Hierarchy")
        eventsheet = workbook.add_worksheet("Events")
        sequencesheet = workbook.add_worksheet("Sequences")
        occursheet = workbook.add_worksheet("Occurences")
        envirsheet = workbook.add_worksheet("Environmental")

        tdformat = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        ###########################################################################################################################
        ### Write project metadata sheet
        project_header_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator',
            'project_qaqc'
        ]
        project_query_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator__full_name',
            'project_qaqc'
        ]
        PMlist = PM.annotate(geome=AsGeoJSON('geomet')).values_list(*project_query_row)

        for col_num, data in enumerate(project_header_row):
            projectsheet.write(0, col_num, data)

        for col_num, data in enumerate(PMlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 1 or row_num == 2 or row_num == 7 or row_num == 8):
                    projectsheet.write(col_num, row_num, data2, tdformat)
                else:
                    projectsheet.write(col_num, row_num, data2)

        ###############################################################################
        ### Write event hierarchy sheet
        eventH_header = [
            'event_hierarchy_name',
            'event_type',
            'description',
            'parent_event_hierarchy',
            'created_on',
            'project_name'
        ]
        eventH_query = [
            'event_hierarchy_name',
            'event_type__name',
            'description',
            'parent_event_hierarchy__event_hierarchy_name',
            'created_on',
            'project_metadata__project_name'
        ]
        EHlist = EH.values_list(*eventH_query)
        for col_num, data in enumerate(eventH_header):
            eventHsheet.write(0, col_num, data)

        for col_num, data in enumerate(EHlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 4):
                    eventHsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventHsheet.write(col_num, row_num, data2)

        ################################################################################
        ### Write Event worksheet
        event_header = [
            'project_name',
            'event_hierarchy',
            'sample_name',
            'parent_event',
            'geom',
            'centroid_lat',
            'centroid_lon',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ### Metadata integrated
            'metadata_tag',
            'md_created_on',
            'metadata_creator',
            'license',
            'geographic_location',
            'locality',
            'geo_loc_name',
            'env_biome',
            'env_package',
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
            'source_mat_id',
            'submitted_to_insdc',
            'investigation_type',
            'isol_growth_condt',
            'lib_size',
            'additional_information'
        ]
        event_query = [
            'event_hierarchy__project_metadata__project_name',
            'event_hierarchy__event_hierarchy_name',
            'sample_name',
            'parent_event__sample_name',
            'geom',
            'Latitude',
            'Longitude',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ## Metadata integrated
            'event_metadata__metadata_tag',
            'event_metadata__md_created_on',
            'event_metadata__metadata_creator__full_name',
            'event_metadata__license',
            'event_metadata__geographic_location__name',
            'event_metadata__locality',
            'event_metadata__geo_loc_name',
            'event_metadata__env_biome',
            'event_metadata__env_package__name',
            'event_metadata__env_feature',
            'event_metadata__env_material',
            'event_metadata__institutionID',
            'event_metadata__nucl_acid_amp',
            'event_metadata__nucl_acid_ext',
            'event_metadata__ref_biomaterial',
            'event_metadata__rel_to_oxygen',
            'event_metadata__rightsHolder',
            'event_metadata__samp_collect_device',
            'event_metadata__samp_store_dur',
            'event_metadata__samp_store_loc',
            'event_metadata__samp_store_temp',
            'event_metadata__samp_vol_we_dna_ext',
            'event_metadata__samplingProtocol',
            'event_metadata__source_mat_id',
            'event_metadata__submitted_to_insdc',
            'event_metadata__investigation_type',
            'event_metadata__isol_growth_condt',
            'event_metadata__lib_size',
            'event_metadata__additional_information'
        ]
        Elist = E.annotate(geom=AsGeoJSON('footprintWKT')).values_list(*event_query)
        for col_num, data in enumerate(event_header):
            eventsheet.write(0, col_num, data)

        for col_num, data in enumerate(Elist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 14):
                    eventsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventsheet.write(col_num, row_num, data2)
        ###########################################################################
        ### Sequences worksheet
        sequence_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        sequence_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        Slist = S.values_list(*sequence_query)
        for col_num, data in enumerate(sequence_header):
            sequencesheet.write(0, col_num, data)

        for col_num, data in enumerate(Slist, 1):
            for row_num, data2 in enumerate(data):
                sequencesheet.write(col_num, row_num, data2)

                #######################################################################################
        ### Occurrence data worksheet
        occur_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'occurrenceID',
            'taxon',
            'occurrence_notes',
            'occurrence_status',
            'occurrence_class',
            'catalog_number',
            'date_identified',
            'other_catalog_numbers',
            'recorded_by'
        ]
        occur_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'occurrenceID',
            'taxon__name',
            'occurrence_notes',
            'occurrence_status',
            'occurrence_class',
            'catalog_number',
            'date_identified',
            'other_catalog_numbers',
            'recorded_by'
        ]
        Olist = O.values_list(*occur_query)
        for col_num, data in enumerate(occur_header):
            occursheet.write(0, col_num, data)

        for col_num, data in enumerate(Olist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 9):
                    occursheet.write(col_num, row_num, data2, tdformat)
                else:
                    occursheet.write(col_num, row_num, data2)

        #######################################################################################
        ### Environmental data worksheet

        envir_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'env_sample_name',
            'link_climate_info',
            'env_variable',
            'env_method',
            'env_units',
            'env_numeric_value',
            'env_text_value'
        ]
        envir_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'env_sample_name',
            'link_climate_info',
            'env_variable__name',
            'env_method__shortname',
            'env_units__name',
            'env_numeric_value',
            'env_text_value'
        ]
        Envlist = Env.values_list(*envir_query)
        for col_num, data in enumerate(envir_header):
            envirsheet.write(0, col_num, data)

        for col_num, data in enumerate(Envlist, 1):
            for row_num, data2 in enumerate(data):
                envirsheet.write(col_num, row_num, data2)

        ################################################################################
        workbook.close()
        output.seek(0)
        curdate = datetime.datetime.now().strftime("%Y-%M-%d")
        filename = 'POLA3R_environmental_' + curdate + '.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        output.close()
        return (response)


###################################################################################################################################################
#### View for returning sequence and event data as an EXCEL spreadsheet
def export_sequences(request):
    user = request.user
    if request.method == 'GET':
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')

        ########################################################################
        ### Authentication checks 

        if user.is_authenticated and user.is_superuser:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__sequences__id__in=IDS).order_by(
                'project_name').distinct('project_name')

            EH = EventHierarchy.objects.filter(event__sequences__id__in=IDS).order_by('event_hierarchy_name').distinct(
                'event_hierarchy_name')

            E = Event.objects.filter(sequences__id__in=IDS).order_by('sample_name').distinct('sample_name')

            S = Sequences.objects.filter(id__in=IDS)

        elif user.is_authenticated:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__sequences__id__in=IDS).filter(Q(
                is_public=True) | Q(project_creator__username=user.username)).order_by('project_name').distinct(
                'project_name')

            EH = EventHierarchy.objects.filter(event__sequences__id__in=IDS).filter(
                Q(project_metadata__is_public=True) | Q(
                    project_metadata__project_creator__username=user.username)).order_by(
                'event_hierarchy_name').distinct('event_hierarchy_name')

            E = Event.objects.filter(sequences__id__in=IDS).filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username)).order_by(
                'sample_name').distinct('sample_name')

            S = Sequences.objects.filter(id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

        else:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__sequences__id__in=IDS).filter(
                Q(is_public=True)).order_by('project_name').distinct('project_name')

            EH = EventHierarchy.objects.filter(event__sequences__id__in=IDS).filter(
                Q(project_metadata__is_public=True)).order_by('event_hierarchy_name').distinct('event_hierarchy_name')

            E = Event.objects.filter(sequences__id__in=IDS).filter(
                Q(event_hierarchy__project_metadata__is_public=True)).order_by('sample_name').distinct('sample_name')

            S = Sequences.objects.filter(id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

        ########################################################################
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        projectsheet = workbook.add_worksheet("Project metadata")
        eventHsheet = workbook.add_worksheet("Event Hierarchy")
        eventsheet = workbook.add_worksheet("Events")
        sequencesheet = workbook.add_worksheet("Sequences")

        tdformat = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        ###########################################################################################################################
        ### Write project metadata sheet
        project_header_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator',
            'project_qaqc'
        ]
        project_query_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator__full_name',
            'project_qaqc'
        ]
        PMlist = PM.annotate(geome=AsGeoJSON('geomet')).values_list(*project_query_row)

        for col_num, data in enumerate(project_header_row):
            projectsheet.write(0, col_num, data)

        for col_num, data in enumerate(PMlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 1 or row_num == 2 or row_num == 7 or row_num == 8):
                    projectsheet.write(col_num, row_num, data2, tdformat)
                else:
                    projectsheet.write(col_num, row_num, data2)

        ###############################################################################
        ### Write event hierarchy sheet
        eventH_header = [
            'event_hierarchy_name',
            'event_type',
            'description',
            'parent_event_hierarchy',
            'created_on',
            'project_name'
        ]
        eventH_query = [
            'event_hierarchy_name',
            'event_type__name',
            'description',
            'parent_event_hierarchy__event_hierarchy_name',
            'created_on',
            'project_metadata__project_name'
        ]
        EHlist = EH.values_list(*eventH_query)
        for col_num, data in enumerate(eventH_header):
            eventHsheet.write(0, col_num, data)

        for col_num, data in enumerate(EHlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 4):
                    eventHsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventHsheet.write(col_num, row_num, data2)

        ################################################################################
        ### Write Event worksheet
        event_header = [
            'project_name',
            'event_hierarchy',
            'sample_name',
            'parent_event',
            'geom',
            'centroid_lat',
            'centroid_lon',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ### Metadata integrated
            'metadata_tag',
            'md_created_on',
            'metadata_creator',
            'license',
            'geographic_location',
            'locality',
            'geo_loc_name',
            'env_biome',
            'env_package',
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
            'source_mat_id',
            'submitted_to_insdc',
            'investigation_type',
            'isol_growth_condt',
            'lib_size',
            'additional_information'
        ]
        event_query = [
            'event_hierarchy__project_metadata__project_name',
            'event_hierarchy__event_hierarchy_name',
            'sample_name',
            'parent_event__sample_name',
            'geom',
            'Latitude',
            'Longitude',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ## Metadata integrated
            'event_metadata__metadata_tag',
            'event_metadata__md_created_on',
            'event_metadata__metadata_creator__full_name',
            'event_metadata__license',
            'event_metadata__geographic_location__name',
            'event_metadata__locality',
            'event_metadata__geo_loc_name',
            'event_metadata__env_biome',
            'event_metadata__env_package__name',
            'event_metadata__env_feature',
            'event_metadata__env_material',
            'event_metadata__institutionID',
            'event_metadata__nucl_acid_amp',
            'event_metadata__nucl_acid_ext',
            'event_metadata__ref_biomaterial',
            'event_metadata__rel_to_oxygen',
            'event_metadata__rightsHolder',
            'event_metadata__samp_collect_device',
            'event_metadata__samp_store_dur',
            'event_metadata__samp_store_loc',
            'event_metadata__samp_store_temp',
            'event_metadata__samp_vol_we_dna_ext',
            'event_metadata__samplingProtocol',
            'event_metadata__source_mat_id',
            'event_metadata__submitted_to_insdc',
            'event_metadata__investigation_type',
            'event_metadata__isol_growth_condt',
            'event_metadata__lib_size',
            'event_metadata__additional_information'
        ]
        Elist = E.annotate(geom=AsGeoJSON('footprintWKT')).values_list(*event_query)
        for col_num, data in enumerate(event_header):
            eventsheet.write(0, col_num, data)

        for col_num, data in enumerate(Elist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 14):
                    eventsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventsheet.write(col_num, row_num, data2)
        ###########################################################################
        ### Sequences worksheet
        sequence_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        sequence_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        Slist = S.values_list(*sequence_query)
        for col_num, data in enumerate(sequence_header):
            sequencesheet.write(0, col_num, data)

        for col_num, data in enumerate(Slist, 1):
            for row_num, data2 in enumerate(data):
                sequencesheet.write(col_num, row_num, data2)

                #######################################################################################

        workbook.close()
        output.seek(0)
        curdate = datetime.datetime.now().strftime("%Y-%M-%d")
        filename = 'POLA3R_sequences_' + curdate + '.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        output.close()
        return (response)


##########################################################################################################################################################
#### This view is to return the spreadsheet when searching by events in the spatial search  - emulates project_metadata 

def export_events(request):
    user = request.user
    if request.method == 'GET':
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')

        ##################################################################################################################
        ##### Authentication checks

        if user.is_authenticated and user.is_superuser:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__id__in=IDS).order_by('project_name').distinct(
                'project_name')

            EH = EventHierarchy.objects.filter(event__id__in=IDS).order_by('event_hierarchy_name').distinct(
                'event_hierarchy_name')

            E = Event.objects.filter(id__in=IDS)

            S = Sequences.objects.filter(event__id__in=IDS)

            O = Occurrence.objects.filter(event__id__in=IDS)

            Env = Environment.objects.filter(event__id__in=IDS)

            G = Geog_Location.objects.filter(sample_metadata__event_sample_metadata__id__in=IDS).order_by(
                'name').distinct('name')

            R = Reference.objects.filter(associated_projects__event_hierarchy__event__id__in=IDS).order_by(
                'full_reference').distinct('full_reference')

            T = Taxa.objects.filter(occurrence__event__id__in=IDS).order_by('name').distinct('name')

        elif user.is_authenticated:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__id__in=IDS).filter(Q(
                is_public=True) | Q(project_creator__username=user.username)).order_by('project_name').distinct(
                'project_name')

            EH = EventHierarchy.objects.filter(event__id__in=IDS).filter(
                Q(project_metadata__is_public=True) | Q(
                    project_metadata__project_creator__username=user.username)).order_by(
                'event_hierarchy_name').distinct('event_hierarchy_name')

            E = Event.objects.filter(id__in=IDS).filter(
                Q(event_hierarchy__project_metadata__is_public=True) | Q(
                    event_hierarchy__project_metadata__project_creator__username=user.username))

            S = Sequences.objects.filter(event__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

            O = Occurrence.objects.filter(event__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

            Env = Environment.objects.filter(event__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True) | Q(
                    event__event_hierarchy__project_metadata__project_creator__username=user.username))

            G = Geog_Location.objects.filter(sample_metadata__event_sample_metadata__id__in=IDS).filter(
                Q(sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__is_public=True) | Q(
                    sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__project_creator__username=user.username)).order_by(
                'name').distinct('name')

            R = Reference.objects.filter(associated_projects__event_hierarchy__event__id__in=IDS).filter(
                Q(associated_projects__is_public=True) | Q(
                    associated_projects__project_creator__username=user.username)).order_by('full_reference').distinct(
                'full_reference')

            T = Taxa.objects.filter(occurrence__event__id__in=IDS).filter(Q(
                occurrence__event__event_hierarchy__project_metadata__is_public=True) | Q(
                occurrence__event__event_hierarchy__project_metadata__project_creator__username=user.username)).order_by(
                'name').distinct('name')

        else:

            PM = ProjectMetadata.objects.filter(event_hierarchy__event__id__in=IDS).filter(Q(is_public=True)).order_by(
                'project_name').distinct('project_name')

            EH = EventHierarchy.objects.filter(event__id__in=IDS).filter(Q(
                project_metadata__is_public=True)).order_by('event_hierarchy_name').distinct('event_hierarchy_name')

            E = Event.objects.filter(id__in=IDS).filter(Q(event_hierarchy__project_metadata__is_public=True))

            S = Sequences.objects.filter(event__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

            O = Occurrence.objects.filter(event__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

            Env = Environment.objects.filter(event__id__in=IDS).filter(
                Q(event__event_hierarchy__project_metadata__is_public=True))

            G = Geog_Location.objects.filter(sample_metadata__event_sample_metadata__id__in=IDS).filter(Q(
                sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__is_public=True)).order_by(
                'name').distinct('name')

            R = Reference.objects.filter(associated_projects__event_hierarchy__event__id__in=IDS).filter(Q(
                associated_projects__is_public=True)).order_by('full_reference').distinct('full_reference')

            T = Taxa.objects.filter(occurrence__event__id__in=IDS).filter(Q(
                occurrence__event__event_hierarchy__project_metadata__is_public=True)).order_by('name').distinct('name')
        #####################################################################################################################

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        projectsheet = workbook.add_worksheet("Project metadata")
        eventHsheet = workbook.add_worksheet("Event Hierarchy")
        eventsheet = workbook.add_worksheet("Events")
        sequencesheet = workbook.add_worksheet("Sequences")
        occursheet = workbook.add_worksheet("Occurrences")
        envirsheet = workbook.add_worksheet("Environmental")
        geomsheet = workbook.add_worksheet("Geography")
        refsheet = workbook.add_worksheet("References")
        taxasheet = workbook.add_worksheet("Taxa")
        tdformat = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        ###########################################################################################################################
        ### Write project metadata sheet
        project_header_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator',
            'project_qaqc'
        ]
        project_query_row = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geome',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator__full_name',
            'project_qaqc'
        ]
        PMlist = PM.annotate(geome=AsGeoJSON('geomet')).values_list(*project_query_row)

        for col_num, data in enumerate(project_header_row):
            projectsheet.write(0, col_num, data)

        for col_num, data in enumerate(PMlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 1 or row_num == 2 or row_num == 7 or row_num == 8):
                    projectsheet.write(col_num, row_num, data2, tdformat)
                else:
                    projectsheet.write(col_num, row_num, data2)

        ###############################################################################
        ### Write event hierarchy sheet
        eventH_header = [
            'event_hierarchy_name',
            'event_type',
            'description',
            'parent_event_hierarchy',
            'created_on',
            'project_name'
        ]
        eventH_query = [
            'event_hierarchy_name',
            'event_type__name',
            'description',
            'parent_event_hierarchy__event_hierarchy_name',
            'created_on',
            'project_metadata__project_name'
        ]
        EHlist = EH.values_list(*eventH_query)
        for col_num, data in enumerate(eventH_header):
            eventHsheet.write(0, col_num, data)

        for col_num, data in enumerate(EHlist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 4):
                    eventHsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventHsheet.write(col_num, row_num, data2)

        ################################################################################
        ### Write Event worksheet
        event_header = [
            'project_name',
            'event_hierarchy',
            'sample_name',
            'parent_event',
            'geom',
            'centroid_lat',
            'centroid_lon',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ### Metadata integrated
            'metadata_tag',
            'md_created_on',
            'metadata_creator',
            'license',
            'geographic_location',
            'locality',
            'geo_loc_name',
            'env_biome',
            'env_package',
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
            'source_mat_id',
            'submitted_to_insdc',
            'investigation_type',
            'isol_growth_condt',
            'lib_size',
            'additional_information'
        ]
        event_query = [
            'event_hierarchy__project_metadata__project_name',
            'event_hierarchy__event_hierarchy_name',
            'sample_name',
            'parent_event__sample_name',
            'geom',
            'Latitude',
            'Longitude',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'eventRemarks',
            'samplingProtocol',
            ## Metadata integrated
            'event_metadata__metadata_tag',
            'event_metadata__md_created_on',
            'event_metadata__metadata_creator__full_name',
            'event_metadata__license',
            'event_metadata__geographic_location__name',
            'event_metadata__locality',
            'event_metadata__geo_loc_name',
            'event_metadata__env_biome',
            'event_metadata__env_package__name',
            'event_metadata__env_feature',
            'event_metadata__env_material',
            'event_metadata__institutionID',
            'event_metadata__nucl_acid_amp',
            'event_metadata__nucl_acid_ext',
            'event_metadata__ref_biomaterial',
            'event_metadata__rel_to_oxygen',
            'event_metadata__rightsHolder',
            'event_metadata__samp_collect_device',
            'event_metadata__samp_store_dur',
            'event_metadata__samp_store_loc',
            'event_metadata__samp_store_temp',
            'event_metadata__samp_vol_we_dna_ext',
            'event_metadata__samplingProtocol',
            'event_metadata__source_mat_id',
            'event_metadata__submitted_to_insdc',
            'event_metadata__investigation_type',
            'event_metadata__isol_growth_condt',
            'event_metadata__lib_size',
            'event_metadata__additional_information'
        ]
        Elist = E.annotate(geom=AsGeoJSON('footprintWKT')).values_list(*event_query)
        for col_num, data in enumerate(event_header):
            eventsheet.write(0, col_num, data)

        for col_num, data in enumerate(Elist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 14):
                    eventsheet.write(col_num, row_num, data2, tdformat)
                else:
                    eventsheet.write(col_num, row_num, data2)
        ###########################################################################
        ### Sequences worksheet
        sequence_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        sequence_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'sequence_name',
            'MID',
            'subspecf_gen_lin',
            'target_gene',
            'target_subfragment',
            'type',
            'primerName_forward',
            'primerName_reverse',
            'primer_forward',
            'primer_reverse',
            'run_type',
            'seqData_url',
            'seqData_accessionNumber',
            'seqData_projectNumber',
            'seqData_runNumber',
            'seqData_sampleNumber',
            'seqData_numberOfBases',
            'seqData_numberOfSequences',
            'ASV_URL'
        ]
        Slist = S.values_list(*sequence_query)
        for col_num, data in enumerate(sequence_header):
            sequencesheet.write(0, col_num, data)

        for col_num, data in enumerate(Slist, 1):
            for row_num, data2 in enumerate(data):
                sequencesheet.write(col_num, row_num, data2)
        #############################################################################
        ### Occurrence sheet
        # occursheet
        occur_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'occurrenceID',
            'taxon',
            'occurrence_notes',
            'occurrence_status',
            'occurrence_class',
            'catalog_number',
            'date_identified',
            'other_catalog_numbers',
            'recorded_by'
        ]
        occur_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'occurrenceID',
            'taxon__name',
            'occurrence_notes',
            'occurrence_status',
            'occurrence_class',
            'catalog_number',
            'date_identified',
            'other_catalog_numbers',
            'recorded_by'
        ]
        Olist = O.values_list(*occur_query)
        for col_num, data in enumerate(occur_header):
            occursheet.write(0, col_num, data)

        for col_num, data in enumerate(Olist, 1):
            for row_num, data2 in enumerate(data):
                if (row_num == 9):
                    occursheet.write(col_num, row_num, data2, tdformat)
                else:
                    occursheet.write(col_num, row_num, data2)
        #######################################################################################
        ### Environmental data worksheet

        envir_header = [
            'project_name',
            'event_hierarchy',
            'event',
            'env_sample_name',
            'link_climate_info',
            'env_variable',
            'env_method',
            'env_units',
            'env_numeric_value',
            'env_text_value'
        ]
        envir_query = [
            'event__event_hierarchy__project_metadata__project_name',
            'event__event_hierarchy__event_hierarchy_name',
            'event__sample_name',
            'env_sample_name',
            'link_climate_info',
            'env_variable__name',
            'env_method__shortname',
            'env_units__name',
            'env_numeric_value',
            'env_text_value'
        ]
        Envlist = Env.values_list(*envir_query)
        for col_num, data in enumerate(envir_header):
            envirsheet.write(0, col_num, data)

        for col_num, data in enumerate(Envlist, 1):
            for row_num, data2 in enumerate(data):
                envirsheet.write(col_num, row_num, data2)
        ########################################################################
        #### Geography worksheet
        geog_header = [
            'name',
            'geog_level',
            'parent_1',
            'parent_2',
            'parent_3',
            'parent_4',
            'parent_5',
            'parent_6',
            'parent_7',
            'parent_8'
        ]
        geog_query = [
            'name',
            'geog_level',
            'parent_geog__name',
            'parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',
            'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name'
        ]
        Glist = G.values_list(*geog_query)
        for col_num, data in enumerate(geog_header):
            geomsheet.write(0, col_num, data)

        for col_num, data in enumerate(Glist, 1):
            for row_num, data2 in enumerate(data):
                geomsheet.write(col_num, row_num, data2)
        ##############################################################################
        ### References worksheet
        ref_header = [
            'full_reference',
            'doi',
            'year',
            'associated_projects'
        ]
        ref_query = [
            'full_reference',
            'doi',
            'year',
            'associated_projects__project_name'
        ]
        Rlist = R.values_list(*ref_query)
        for col_num, data in enumerate(ref_header):
            refsheet.write(0, col_num, data)

        for col_num, data in enumerate(Rlist, 1):
            for row_num, data2 in enumerate(data):
                refsheet.write(col_num, row_num, data2)
        #####################################################################################
        ### Taxa worksheet
        taxa_header = [
            'name',
            'TaxonRank',
            'taxonID',
            'parent_1',
            'parent_2',
            'parent_3',
            'parent_4',
            'parent_5',
            'parent_6',
            'parent_7',
            'parent_8',
            'parent_9',
            'parent_10',
            'parent_11',
            'parent_12',
            'parent_13',
            'parent_14',
            'parent_15',
            'parent_16'
        ]
        taxa_query = [
            'name',
            'TaxonRank',
            'taxonID',
            'parent_taxa__name',
            'parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
            'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name'
        ]
        Tlist = T.values_list(*taxa_query)
        for col_num, data in enumerate(taxa_header):
            taxasheet.write(0, col_num, data)

        for col_num, data in enumerate(Tlist, 1):
            for row_num, data2 in enumerate(data):
                taxasheet.write(col_num, row_num, data2)

        ################################################################################
        workbook.close()
        output.seek(0)
        curdate = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = 'POLA3R_events_' + curdate + '.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        output.close()
        return (response)


def api_reference(request):
    return render(request, 'rest_framework/api_reference.html')
