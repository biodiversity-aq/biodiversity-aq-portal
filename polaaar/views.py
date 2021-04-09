from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.core.cache import cache
from django.core.serializers import serialize
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import Q, Count, Min
from django.contrib.gis.db.models.functions import AsGeoJSON, Centroid
from django.views import generic

from .forms import EmailForm, ProjectSearchForm, EnvironmentSearchForm, SequenceSearchForm
from django.core.mail import EmailMessage
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, generics
from biodiversity.decorators import verify_recaptcha
from polaaar.serializers import *
from polaaar.models import Reference

import xlsxwriter
import io
import logging
import datetime
import zipfile
import os

# Get an instance of a logger
logger = logging.getLogger(__name__)


def home(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'polaaar', 'amplicon_image.png')
    if os.path.isfile(file_path):
        amplicon_img = os.path.join(settings.MEDIA_URL, 'polaaar', 'amplicon_image.png')
    else:
        amplicon_img = False
    return render(request, 'polaaar/polaaar_home.html',
                  {'geoserver_host': settings.GEOSERVER_HOST, 'amplicon_img': amplicon_img})


def api_reference(request):
    return render(request, 'polaaar/api_reference.html')


#########################################################
### DJANGO Search views
##########

def get_queryset_from_env_search_form(request):
    """
    Return QuerySet for Environment Search
    :param request: HttpRequest GET object
    :return: QuerySet of Environment class
    """
    form = EnvironmentSearchForm(request)
    qs = Environment.objects.filter(event__event_hierarchy__project_metadata__is_public=True) \
        .prefetch_related('event__sequences', 'event__project_metadata') \
        .select_related('event', 'env_variable', 'env_units') \
        .order_by('env_variable')
    if form.is_valid():
        variable = form.cleaned_data.get('variable')  # required
        text = form.cleaned_data.get('text', '')
        min_value = form.cleaned_data.get('min_value')
        max_value = form.cleaned_data.get('max_value')
        var_type = variable.var_type

        if var_type == 'TXT':
            query = {"event__event_hierarchy__project_metadata__is_public": True, "env_variable": variable.id,
                     "env_text_value__icontains": text}
        elif var_type == 'NUM' and min_value and max_value:
            query = {"event__event_hierarchy__project_metadata__is_public": True, "env_variable": variable.id,
                     "env_numeric_value__gte": min_value, "env_numeric_value__lte": max_value}
        elif var_type == 'NUM' and min_value:
            query = {"event__event_hierarchy__project_metadata__is_public": True, "env_variable": variable.id,
                     "env_numeric_value__gte": min_value}
        elif var_type == 'NUM' and max_value:
            query = {"event__event_hierarchy__project_metadata__is_public": True, "env_variable": variable.id,
                     "env_numeric_value__lte": max_value}
        else:  # only var_id
            query = {"event__event_hierarchy__project_metadata__is_public": True, "env_variable": variable.id}
        qs = Environment.objects.prefetch_related('event__sequences', 'event__project_metadata') \
            .select_related('event', 'env_variable', 'env_units').filter(**query)
    return qs


class EnvironmentListView(generic.ListView):
    """
    List the search results for Environment instances
    """
    template_name = 'polaaar/environment_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = get_queryset_from_env_search_form(self.request.GET)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EnvironmentSearchForm(self.request.GET)
        events = Event.objects.filter(environment__in=self.get_queryset()).annotate(count=Count('id')).order_by()\
            .prefetch_related('sequences')
        context['event_geojson'] = serialize('geojson', events, geometry_field='footprintWKT', fields=('sequences',))
        return context


class SequenceListView(generic.ListView):
    """
    List the search results for Sequence instances
    """
    template_name = 'polaaar/sequence_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = Sequences.objects.filter(event__project_metadata__is_public=True)\
            .select_related('event__project_metadata')
        form = SequenceSearchForm(self.request.GET)
        if form.is_valid():
            search_term = form.cleaned_data.get('q')
            if search_term:  # return queryset if there is no search term
                vector = SearchVector('MID', 'target_gene', 'target_subfragment', 'type', 'primerName_forward',
                                      'primerName_reverse', 'run_type')
                query = SearchQuery(search_term)
                # filter for ProjectMetadata which is public AND (project_name contains search term or abstract
                # contains search term)
                qs = Sequences.objects.annotate(rank=SearchRank(vector, query)) \
                    .filter(event__project_metadata__is_public=True, rank__gte=0.01).order_by('-rank')\
                    .select_related('event__project_metadata')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SequenceSearchForm(self.request.GET)
        return context


def spatial_searching(request):
    qs_results = Event.objects.annotate(geom=AsGeoJSON(Centroid('footprintWKT'))).filter(
        Q(event_hierarchy__project_metadata__is_public=True))
    return render(request, 'polaaar/spatial_search.html', {'qs_results': qs_results})


def spatial_search_table(request):
    if request.method == "GET":
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')
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
        print(filenames)
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

    pass


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
            submitted_by = form.cleaned_data.get('email')
            document = form.cleaned_data.get('document')
            subject = '[POLA3R Data Submission]{}'.format(subject)
            message = '{}\nSubmitted by {}'.format(message, submitted_by)
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
        'project_contact': ['exact', 'icontains'],
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
        queryset = EventHierarchy.objects.filter(Q(project_metadata__is_public=True))
        return queryset


class OccurrenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OccurrenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'occurrenceID': ['exact', 'istartswith', 'icontains']
    }

    def get_queryset(self):
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
        queryset = Event.objects.filter(Q(event_hierarchy__project_metadata__is_public=True))
        return queryset


class GeogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GeogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'name': ['exact']
    }

    def get_queryset(self):
        queryset = Geog_Location.objects.filter(Q(
            sample_metadata__event_sample_metadata__event_hierarchy__project_metadata__is_public=True)).order_by(
            'name').distinct('name')
        return queryset


class EnvironmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'id': ['exact', 'in'],
    }

    def get_queryset(self):
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
        queryset = Environment.objects.filter(Q(event__event_hierarchy__project_metadata__is_public=True))
        return queryset


###################################################################################################################################################################################
### Project level XLSX download
### This creates an XLSX sheet with multiple worksheets 

#########################################################################################################################################
####### THESE ARE ALL 'GET' CALLS RIGHT NOW, BUT MAY NEED TO SWITCH TO POST CALLS IF THE NUMBER OF EVENTS IS TOO HIGH #####################
#########################################################################################################################################

def export_projects(request):
    if request.method == 'GET':
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')

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
            'project_qaqc',
            'project_contact',
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
            'project_qaqc',
            'project_contact',
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
    if request.method == 'GET':
        env_qs = get_queryset_from_env_search_form(request.GET)

        ###########################################################################################################
        #### Authentication checks

        PM = ProjectMetadata.objects.filter(event_hierarchy__event__environment__in=env_qs).filter(
            Q(is_public=True)).annotate(Count('id')).order_by()

        EH = EventHierarchy.objects.filter(event__environment__in=env_qs).filter(
            Q(project_metadata__is_public=True)).annotate(Count('event_hierarchy_name')).order_by()

        E = Event.objects.filter(environment__in=env_qs).filter(Q(
            event_hierarchy__project_metadata__is_public=True)).annotate(Count('sample_name')).order_by()

        S = Sequences.objects.filter(event__environment__in=env_qs).filter(Q(
            event__event_hierarchy__project_metadata__is_public=True)).annotate(Count('sequence_name')).order_by()

        O = Occurrence.objects.filter(event__environment__in=env_qs).filter(
            Q(event__event_hierarchy__project_metadata__is_public=True)).annotate(Count('occurrenceID')).order_by()

        Env = env_qs
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
    if request.method == 'GET':
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')

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
        filename = 'POLA3R_sequences_metadata_' + curdate + '.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        output.close()
        return response


##########################################################################################################################################################
#### This view is to return the spreadsheet when searching by events in the spatial search  - emulates project_metadata 

def export_events(request):
    if request.method == 'GET':
        IDS = request.GET.getlist('id')
        IDS = IDS[0].split(',')

        ##################################################################################################################
        ##### Authentication checks

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
            'project_qaqc',
            'project_contact',
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
            'project_qaqc',
            'project_contact',
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
        return response


class ProjectMetadataListView(generic.ListView):
    """
    List the search results for ProjectMetadata instances
    """
    template_name = 'polaaar/projectmetadata_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = ProjectMetadata.objects.filter(is_public=True)
        form = ProjectSearchForm(self.request.GET)
        if form.is_valid():
            search_term = form.cleaned_data.get('q')
            if search_term:  # return queryset if there is no search term
                vector = SearchVector('project_name', 'abstract')
                query = SearchQuery(search_term)
                # filter for ProjectMetadata which is public AND (project_name contains search term or abstract
                # contains search term)
                qs = ProjectMetadata.objects.annotate(rank=SearchRank(vector, query)) \
                    .filter(is_public=True, rank__gte=0.01).order_by('-rank')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProjectSearchForm(self.request.GET)
        id_list = self.get_queryset().values_list('id', flat=True)
        context['id_list'] = ','.join(map(str, id_list))
        return context


def project_metadata_detail(request, pk):
    """
    ProjectMetadata detail page, displays statistics of various variables related to project.
    :param request: http GET request
    :param pk: pk of the ProjectMetadata object
    :return: HttpResponse of the ProjectMetadata with statistics in the context
    """
    get_object_or_404(ProjectMetadata, pk=pk)
    project = ProjectMetadata.objects.get(pk=pk)
    cache_key = 'project{}_{}'.format(project.id, project.updated_on)
    project_cache = cache.get(cache_key)
    if not project_cache:
        context = dict()
        event = Event.objects.filter(event_hierarchy__project_metadata=project)
        mof = Variable.objects.filter(environment__event__event_hierarchy__project_metadata=project)
        sequence = Sequences.objects.filter(event__event_hierarchy__project_metadata=project)
        sample = SampleMetadata.objects.filter(event_sample_metadata__event_hierarchy__project_metadata=project)
        ref = Reference.objects.filter(associated_projects=project)

        event_per_year = event.exclude(collection_year__isnull=True).values('collection_year').annotate(
            count=Count('collection_year')).order_by()
        event_per_month = event.exclude(collection_month__isnull=True).values('collection_month').annotate(
            count=Count('collection_month')).order_by()
        sample_geo_loc_name = sample.exclude(geo_loc_name__isnull=True).values('geo_loc_name').annotate(
            count=Count('geo_loc_name')).order_by()
        sample_env_biome = sample.exclude(env_biome__isnull=True).values('env_biome').annotate(
            count=Count('env_biome')).order_by()
        mof_name = mof.exclude(name__isnull=True).values('name').annotate(count=Count('name')).order_by()
        seq_target_gene = sequence.exclude(target_gene__isnull=True).values('target_gene').annotate(
            count=Count('target_gene')).order_by()
        seq_target_subfg = sequence.exclude(target_subfragment__isnull=True).values('target_subfragment').annotate(
            count=Count('target_subfragment')).order_by()
        seq_type = sequence.exclude(type__isnull=True).values('type').annotate(count=Count('type')).order_by()
        seq_run_type = sequence.exclude(run_type__isnull=True).values('run_type').annotate(
            count=Count('run_type')).order_by()
        seq_seqData_projectNumber = sequence.exclude(seqData_projectNumber__isnull=True).values(
            'seqData_projectNumber').annotate(count=Count('seqData_projectNumber')).order_by()
        try:
            min_lat = event.values('Latitude').annotate(min=Min('Latitude')).order_by().values('min')[0].get('min')
        except IndexError:
            min_lat = 0
        context['project'] = project
        context['license'] = project.get_license()
        context['citation'] = project.get_citation()
        context['event_count'] = event.count()
        context['event_per_year'] = event_per_year
        context['event_per_month'] = event_per_month
        context['sample_count'] = sample.count()
        context['sample_geo_loc_name'] = sample_geo_loc_name
        context['sample_env_biome'] = sample_env_biome
        context['mof_count'] = mof.count()
        context['mof_name'] = mof_name
        context['seq_count'] = sequence.count()
        context['seq_target_gene'] = seq_target_gene
        context['seq_target_subfg'] = seq_target_subfg
        context['seq_type'] = seq_type
        context['seq_run_type'] = seq_run_type
        context['seq_seqData_projectNumber'] = seq_seqData_projectNumber
        context['min_lat'] = min_lat
        context['ref'] = ref
        context['geoserver_host'] = settings.GEOSERVER_HOST
        cache.set(cache_key, context)  # cache the context if not found
    else:
        context = project_cache
    response = render(request, template_name='polaaar/projectmetadata_detail.html', context=context)
    return response
