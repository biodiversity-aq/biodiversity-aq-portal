from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from accounts.models import *
from .models import *
from rest_framework import serializers


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = [
            'full_reference',
            'doi',
            'year',
        ]


class SequencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequences
        fields = [
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
            'seqData_numberOfSequences'
        ]


class sampling_methodSerializer(serializers.ModelSerializer):
    class Meta:
        model = sampling_method
        fields = [
            'shortname',
            'description'
        ]


class unitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = units
        fields = [
            'name',
            'html_tag'
        ]


class VariableSerializer(serializers.ModelSerializer):
    var_units = serializers.StringRelatedField(many=True)
    method = serializers.StringRelatedField(many=True)

    class Meta:
        model = Variable
        fields = [
            'name',
            'var_units',
            'method',
            'var_type'
        ]


class EnvironmentSerializer(serializers.ModelSerializer):
    env_variable = serializers.StringRelatedField(many=False)
    env_method = serializers.StringRelatedField(many=False)
    env_units = serializers.StringRelatedField(many=False)

    class Meta:
        model = Environment
        fields = [
            'id',
            'env_sample_name',
            'created_at',
            'link_climate_info',
            'env_variable',
            'env_method',
            'env_units',
            'env_numeric_value',
            'env_text_value'
        ]


#########################################################################################################
class GeogSerializer(serializers.ModelSerializer):
    parent_geog = serializers.StringRelatedField(many=False)

    class Meta:
        model = Geog_Location
        fields = [
            'name',
            'geog_level',
            'parent_geog'
        ]


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = [
            'name']


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = package
        fields = [
            'name']


class SampleMetadataSerializer(serializers.ModelSerializer):
    metadata_creator = serializers.StringRelatedField(many=False)
    geographic_location = GeogSerializer(many=False, read_only=True)
    env_package = serializers.StringRelatedField(many=False)
    sequence = SequencesSerializer(many=True, read_only=True)

    class Meta:
        model = SampleMetadata
        fields = [
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
            'samplingProtocol',
            'source_mat_id',
            'submitted_to_insdc',
            'investigation_type',
            'isol_growth_condt',
            'lib_size',
            'sequence',
            'additional_information'
        ]


######################################################################################


class TaxaSerializer(serializers.ModelSerializer):
    parent_taxa = serializers.StringRelatedField(many=False)

    # parent_taxa = self(many=False,read_only=True)
    class Meta:
        model = Taxa
        fields = [
            'name',
            'TaxonRank',
            'taxonID',
            'parent_taxa'
        ]


class OccurrenceSerializer(serializers.ModelSerializer):
    taxon = TaxaSerializer(many=False, read_only=True)
    associated_sequences = SequencesSerializer(many=True, read_only=True)

    class Meta:
        model = Occurrence
        fields = [
            'occurrenceID',
            'taxon',
            'occurrence_notes',
            'occurrence_status',
            'occurrence_class',
            'catalog_number',
            'date_identified',
            'other_catalog_numbers',
            'recorded_by',
            'associated_sequences']


class EventSerializer(serializers.ModelSerializer):
    occurrence = OccurrenceSerializer(many=True, read_only=True)
    environment = EnvironmentSerializer(many=True, read_only=True)
    parent_event = serializers.StringRelatedField(many=False)
    event_metadata = SampleMetadataSerializer(many=False, read_only=True)

    class Meta:
        model = Event
        fields = [
            'parent_event',
            'footprintWKT',
            'eventRemarks',
            'sample_name',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'samplingProtocol',
            'event_metadata',
            'occurrence',
            'environment',
            'metadata_exists',
            'occurrence_exists',
            'environment_exists']


class EventHierarchySerializer(serializers.ModelSerializer):
    # project_metadata = ProjectMetadataSerializer(many=False,read_only=True)
    event = EventSerializer(many=True, read_only=True)
    # event = serializers.HyperlinkedRelatedField(
    #    many=True,
    #    read_only=True,
    #    view_name='event-detail'
    # )
    event_type = serializers.StringRelatedField(many=False)
    parent_event = serializers.StringRelatedField(many=False)
    event_creator = serializers.StringRelatedField(many=False)

    class Meta:
        model = EventHierarchy
        fields = [
            'url',
            'event_hierarchy_name',
            'event_type',
            'description',
            'parent_event',
            'event_creator',
            'created_on',
            'updated_on',
            'event']


class ProjectMetadataSerializer(serializers.ModelSerializer):
    associated_references = ReferenceSerializer(many=True, read_only=True)
    # event_hierarchy = EventHierarchySerializer(many=True,read_only=True)
    event_hierarchy = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='eventhierarchy-detail'
    )

    class Meta:
        model = ProjectMetadata
        fields = [
            'url',
            'project_name',
            'project_contact',
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
            'project_qaqc',
            'event_hierarchy']
        # ,
        pandas_index = ['associated_references']
        pandas_unstacked_header = [
            'url',
            'project_name',
            'project_contact',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'geomet',
            'is_public',
            'associated_media',
            'created_on',
            'updated_on',
            'project_creator',
            'project_qaqc']


##############################################
#####################
## Special serializers for downloading specific sequences and keeping links to projects, events


class SeqProjectMetadataSerializer(serializers.ModelSerializer):
    project_creator = serializers.StringRelatedField(many=False)

    class Meta:
        model = ProjectMetadata
        fields = [
            'project_name',
            'start_date',
            'end_date',
            'EML_URL',
            'abstract',
            'created_on',
            'project_creator']


class SeqEventHierarchySerializer(serializers.ModelSerializer):
    project_metadata = SeqProjectMetadataSerializer(many=False, read_only=True)
    event_type = serializers.StringRelatedField(many=False)
    parent_event = serializers.StringRelatedField(many=False)
    event_creator = serializers.StringRelatedField(many=False)

    class Meta:
        model = EventHierarchy
        fields = [
            'event_hierarchy_name',
            'event_type',
            'description',
            'parent_event',
            'event_creator',
            'created_on',
            'project_metadata']


class SeqEventSerializer(serializers.ModelSerializer):
    event_hierarchy = SeqEventHierarchySerializer(many=False, read_only=True)
    parent_event = serializers.StringRelatedField(many=False)
    event_metadata = SampleMetadataSerializer(many=False, read_only=True)

    class Meta:
        model = Event
        fields = [
            'sample_name',
            'parent_event',
            'footprintWKT',
            'Latitude',
            'Longitude',
            'eventRemarks',
            'collection_year',
            'collection_month',
            'collection_day',
            'collection_time',
            'samplingProtocol',
            'event_metadata',
            'event_hierarchy']


@swagger_auto_schema(methods=['get'], auto_schema=None)
@api_view(['GET'])
class SequencesSerializer2(serializers.ModelSerializer):
    event = SeqEventSerializer(many=False, read_only=True)

    class Meta:
        model = Sequences
        fields = [
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
            'seqData_numberOfSequences'
        ]


######################################################################################
## Special serializers for looking up environmental data
@swagger_auto_schema(methods=['get'], auto_schema=None)
@api_view(['GET'])
class EnvironmentSerializer2(serializers.ModelSerializer):
    env_variable = serializers.StringRelatedField(many=False)
    env_method = serializers.StringRelatedField(many=False)
    env_units = serializers.StringRelatedField(many=False)
    event = SeqEventSerializer(many=False, read_only=True)

    class Meta:
        model = Environment
        fields = [
            'event',
            'env_sample_name',
            'created_at',
            'link_climate_info',
            'env_variable',
            'env_method',
            'env_units',
            'env_numeric_value',
            'env_text_value'
        ]
