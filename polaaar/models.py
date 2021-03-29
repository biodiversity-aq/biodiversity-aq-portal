from __future__ import unicode_literals

import datetime
import json

import requests
import defusedxml.ElementTree as ET
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.gis.gdal import *
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from accounts.models import UserProfile

### Hard-wiring in choices for continent
CONTINENTS = [
    ('NA', 'North America'),
    ('SA', 'South America'),
    ('EU', 'Europe'),
    ('OC', 'Oceania'),
    ('AN', 'Antarctica'),
    ('AS', 'Asia'),
    ('AF', 'Africa')
]

############################################################################################
#### Taxonomy model block

## This block defines the db table (model) for the taxonomy.
## We have opted to do this as a recursive table which is an efficient way to handle non-specific
## endpoints. This way, the data can be linked at any taxa level.

TAXA = (
    ('superKingdom', 'superKingdom'),
    ('Kingdom', 'Kingdom'),
    ('SubKingdom', 'SubKingdom'),
    ('Phylum', 'Phylum'),
    ('SubPhylum', 'SubPhylum'),
    ('Class', 'Class'),
    ('SubClass', 'SubClass'),
    ('Order', 'Order'),
    ('SubOrder', 'SubOrder'),
    ('Family', 'Family'),
    ('SubFamily', 'SubFamily'),
    ('Genus', 'Genus'),
    ('SubGenus', 'SubGenus'),
    ('Species', 'Species'),
    ('SubSpecies', 'SubSpecies'),
    ('Strain', 'Strain')
)


class Taxa(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True,
                            help_text="the name and subject or a record (line) in a table")
    TaxonRank = models.CharField(max_length=100, choices=TAXA, blank=True, null=True,
                                 help_text="http://rs.tdwg.org/dwc/terms/verbatimTaxonRank")
    taxonID = models.CharField(max_length=100, blank=True, null=True,
                               help_text="http://rs.tdwg.org/dwc/terms/scientificNameID")  ## From WORMS
    ## this is the recursive link to the table. We allow this to be null and blank
    ## because at the top level (Kingdom), we wouldn't have a parent
    parent_taxa = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='TaxonName', blank=True,
                                    null=True)

    ### Add constraint to not point to its own rank :) 

    def __str__(self):
        return self.TaxonRank + ': ' + self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Taxa'


##### End of Taxonomy model block
#####################################################################################################

#####################################################################################################
#### Biome levels ####

##### BIOME COMMENTED OUT ON FEB 24 2020

## Much like the species tables, we use a recursive model because the endpoint of the biome is 
## ambiguous. This means the user can select any biome. We will set the values of this ourselves
## and allow users to select from it. Levels are hierarchical to each other. I.E. Level 2 is a child of Level 1
## Level 3 is a child to Level 2, etc... 

# BIOME_LEVELS = (
#    ('L1',"Level_1"),
#    ('L2',"Level_2"),
#    ('L3',"Level_3"),
#    ('L4',"Level_4"),
#    ('L5',"Level_5")
#    )


# class Biome(models.Model):
#    name = models.CharField(max_length=300,null=True,blank=True)
#    biome_level = models.CharField(max_length=300,choices=BIOME_LEVELS)
#    parent_biome = models.ForeignKey('self',on_delete=models.DO_NOTHING,related_name='BiomeName',blank=True,null=True)

#    def __str__(self):
#        return self.biome_level+': '+self.name  
#    class Meta:
#        ordering=['name']

##### End of Biome model block
#####################################################################################################
#### Geographical location table

GEOG_LEVELS = (
    ('continent', 'continent'),
    ('waterBody', 'waterBody'),
    ('country', 'country'),
    ('islandGroup', 'islandGroup'),
    ('island', 'island'),
    ('stateProvince', 'stateProvince'),
    ('county', 'county'),
    ('municipality', 'municipality'),
    ('locality', 'locality'),
)


class Geog_Location(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True,
                            help_text="The name and subject or a record (line) in a table")
    geog_level = models.CharField(max_length=300, choices=GEOG_LEVELS,
                                  help_text="A level indicating the geographical scale or a geographic name (e.g. continent; country; province; city)")
    parent_geog = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='GeogName', blank=True, null=True,
                                    help_text="Foreign key to (parent) Geog_Location table")

    def __str__(self):
        return self.geog_level + ': ' + self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Geography"
        verbose_name_plural = "Geographic Locations"


#####################################################################################################
#### MIxS package table

class package(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True,
                            help_text="The name and subject or a record (line) in a table")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'MiXS packages'
        verbose_name_plural = 'MiXS packages'


##### End of MIxS package model block
#####################################################################################################
#### References tables

### This is a simple references table. We have kept this simple here because there will be generally low
### volumes of data coming in, and therefore it can easily be cleaned if need be. 

class Reference(models.Model):
    full_reference = models.TextField(
        help_text="Citation that form a bibliography on literature related / used in the dataset")  ### The full reference
    doi = models.CharField(max_length=255, blank=True, null=True,
                           help_text="doi of the literature related / used in the dataset")  ### doi of the reference if known
    year = models.IntegerField(
        help_text="The year of the literature related / used in the dataset")  ### The year the reference was published
    associated_projects = models.ManyToManyField(_("ProjectMetadata"), related_name='associated_references', blank=True,
                                                 help_text="Foreign key to the ProjectMetadata table")

    def __str__(self):
        return self.full_reference

    class Meta:
        ordering = ['-year']  ### Order this by year (descending), listing most recent first


##### End of References models block
#####################################################################################################


######################################################################################################
### ParentEvents tables
# The ParentEvent table defines the broad parameters from which the samples were taken. This is done via another
# recursive model, allowing the user to define the hierarchy of the sampling. 
# For example, a top level parentevent could be a project, next a cruise, then a transect. 

## We're not sure what kind of events we could have, so we'll create a table to make it easy to add these
class EventType(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True,
                            help_text="The name and subject or a record (line) in a table")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# fsa = FileSystemStorage(location='/media/project_files')
class ProjectMetadata(models.Model):
    resource_url = models.TextField(blank=True, null=True,
                                    help_text='Resource link of this dataset, preferrably points to EML resource page')
    project_name = models.CharField(max_length=255, blank=True, null=True,
                                    help_text="Name of the project within which the sequencing was organized")
    start_date = models.DateField(blank=True, null=True, help_text="Start date of the project")
    end_date = models.DateField(blank=True, null=True, help_text="End date of the project")
    EML_URL = models.URLField(blank=True, null=True,
                              help_text="The url of to the project metadata's EML file on the IPT or GBIF")  ## URL to GBIF generated EML file
    abstract = models.TextField(blank=True, null=True,
                                help_text="https://eml.ecoinformatics.org/schema/eml-resource_xsd.html#ResourceGroup_abstract")  ## Abstract for the event, if available

    geomet = models.PolygonField(srid=4326, blank=True, null=True,
                                 help_text="https://eml.ecoinformatics.org/schema/eml-coverage_xsd.html#GeographicCoverage_boundingCoordinates")

    is_public = models.BooleanField(help_text="Whether a the data of a project is public or embargoed")

    associated_media = models.TextField(blank=True, null=True,
                                        help_text="http://rs.tdwg.org/dwc/terms/associatedReferences")
    created_on = models.DateField(
        help_text="The date on which the resource created recommended best practice is to use an encoding scheme; such as ISO 8601:2004(E)")
    updated_on = models.DateField(auto_now=True, help_text="The most recent date on which the resource was changed.")
    project_contact = models.TextField(blank=True, null=True,
                                       help_text="https://eml.ecoinformatics.org/schema/eml-dataset_xsd.html#DatasetType_contact")
    project_creator = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.DO_NOTHING,
                                        help_text="The user who created this record.")

    project_qaqc = models.BooleanField(blank=True, null=True,
                                       help_text="Whether or not a dataset has been Quality Controlled")

    def __str__(self):
        return self.project_name

    def get_eml(self):
        r = requests.get(self.EML_URL).content
        etree = ET.fromstring(r)
        return etree

    def get_license(self):
        """
        Get license from eml
        """
        etree = self.get_eml()
        project_license_dict = etree.find('.//intellectualRights/para/ulink')
        project_license = project_license_dict.get('url')
        return project_license

    def get_citation(self):
        """
        Get citation from eml
        """
        etree = self.get_eml()
        citation_ipt = etree.find('./additionalMetadata/metadata/gbif/citation').text
        if citation_ipt:
            now = datetime.datetime.now().date()
            pola3r = "(Available: Polar 'Omics Links to Antarctic, Arctic and Alpine Research. Antarctic Biodiversity Portal. Scientific Committee for Antarctic Research. www.biodiversity.aq/pola3r. Accessed: {})".format(
                now)
            citation = "{} {}".format(citation_ipt, pola3r)
        else:
            citation = None
        return citation

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Project metadata'
        verbose_name_plural = 'Project metadata'


####################################################################################################################

## Change to EventHierarchy

class EventHierarchy(models.Model):
    event_hierarchy_name = models.CharField(max_length=255, blank=True, null=True,
                                            help_text="The original sample name that can be used to identify the material taken in the field.")  ## User's project name or cruise name, etc...
    event_type = models.ForeignKey(_("EventType"), related_name='eventtype',
                                   on_delete=models.DO_NOTHING,
                                   help_text="Foreign key to EventType table")  ## Drawn from the Event_type table

    description = models.TextField(blank=True, null=True,
                                   help_text="A description of the sample as it was taken from the natural environment")  ## Description of the event

    parent_event_hierarchy = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='EventRank',
                                               blank=True, null=True, help_text="Foreign key to EventHierarchy table")
    event_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, help_text="The user who created this record")
    created_on = models.DateField(
        help_text="The date on which the resource created recommended best practice is to use an encoding scheme; such as ISO 8601:2004(E)")
    updated_on = models.DateField(auto_now=True, help_text="The most recent date on which the resource was changed")

    project_metadata = models.ForeignKey(_("ProjectMetadata"), related_name='event_hierarchy', blank=True, null=True,
                                         on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {}'.format(self.event_type.name, self.event_hierarchy_name)

    class Meta:
        ordering = ['event_hierarchy_name']
        verbose_name = 'Event hierarchy'
        verbose_name_plural = 'Event hierarchy'


#### End of parent event models block
####################################################################################################
### Event table block 

## This table refers to specific samples taken, and is recursive - so if a sample gets SUBSAMPLED
## then a new event (sample) can be defined with the original sample as a parent.
MONTHS = (
    (1, '01'),
    (2, '02'),
    (3, '03'),
    (4, '04'),
    (5, '05'),
    (6, '06'),
    (7, '07'),
    (8, '08'),
    (9, '09'),
    (10, '10'),
    (11, '11'),
    (12, '12')
)


class Event(models.Model):
    footprintWKT = models.GeometryField(srid=4326, blank=True, null=True,
                                        help_text="http://rs.tdwg.org/dwc/terms/footprintWKT")

    Latitude = models.DecimalField(decimal_places=5, max_digits=10, blank=True, null=True,
                                   help_text="http://rs.tdwg.org/dwc/terms/decimalLatitude")
    Longitude = models.DecimalField(decimal_places=5, max_digits=10, blank=True, null=True,
                                    help_text="http://rs.tdwg.org/dwc/terms/decimalLongitude")

    eventRemarks = models.TextField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/terms/eventRemarks")
    sample_name = models.CharField(max_length=255, blank=True,
                                   null=True,
                                   help_text="The original sample name that can be used to identify the material taken in the field.")  # ,unique=True)   ### Unique value      ## User provided id for sample

    collection_year = models.IntegerField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/terms/year")
    collection_month = models.IntegerField(blank=True, null=True, choices=MONTHS,
                                           help_text="http://rs.tdwg.org/dwc/terms/month")
    collection_day = models.IntegerField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/terms/day")

    collection_time = models.TimeField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/terms/eventTime")
    event_hierarchy = models.ForeignKey(_("EventHierarchy"), related_name='event', on_delete=models.CASCADE,
                                        help_text="Foreign key to EventHierarchy record")
    ### Sample is a recursive table, and can be sub-sampled (in other words, it refers back to itself so you can build on itself)    
    parent_event = models.ForeignKey('self',
                                     on_delete=models.DO_NOTHING,
                                     blank=True,
                                     null=True, help_text="Foreign key to a (parent) Event table")

    samplingProtocol = models.TextField(blank=True, null=True,
                                        help_text="http://rs.tdwg.org/dwc/terms/samplingProtocol")

    event_metadata = models.ForeignKey(_("SampleMetadata"), related_name='event_sample_metadata', blank=True, null=True,
                                       on_delete=models.CASCADE, help_text="Foreign key to SampleMetadata table")

    metadata_exists = models.BooleanField(blank=True, null=True,
                                          help_text="Whether or not there is SampleMetadata associated to this Event record")
    occurrence_exists = models.BooleanField(blank=True, null=True,
                                            help_text="Whether or not there is Occurrence associated to this Event record")
    environment_exists = models.BooleanField(blank=True, null=True,
                                             help_text="Whether or not there is Environment associated to this Event record")
    sequences_exists = models.BooleanField(blank=True, null=True,
                                           help_text="Whether or not there is Sequence associated to this Event record")
    # add ProjectMetadata here because it is easier to query for the map
    project_metadata = models.ForeignKey(ProjectMetadata, blank=True, null=True, on_delete=models.CASCADE,
                                         help_text='Foreign key to ProjectMetadata record')

    def save(self, *args, **kwargs):
        coords = json.loads(GEOSGeometry(self.footprintWKT).centroid.json)["coordinates"]
        self.Latitude = coords[0]
        self.Longitude = coords[1]
        super(Event, self).save(*args, **kwargs)

    @property
    def popupContent(self):
        return '<p style="margin-top:0px;margin-bottom:0px;"><strong>Project name:\
     {}</strong></p><p style="margin-top:0px;margin-bottom:0px;">Creator: {}</p>\
     <p style="margin-top:0px;margin-bottom:0px;">Sample name: {}</p>'.format(
            self.event_hierarchy.project_metadata.project_name,
            self.event_hierarchy.project_metadata.project_creator.full_name,
            self.sample_name)

    def __str__(self):
        return self.sample_name

    class Meta:
        ordering = ['-collection_year', '-collection_month', '-collection_day', '-collection_time']


#### End of event models block
####################################################################################################
### Occurrences block

### This is a table which records any occurrences associated with a sample. 
class Occurrence(models.Model):
    occurrenceID = models.CharField(max_length=255, blank=True, null=True,
                                    help_text="http://rs.tdwg.org/dwc/terms/occurrenceID")
    taxon = models.ForeignKey(_('Taxa'), related_name='occurrence', on_delete=models.DO_NOTHING,
                              help_text="Foreign key to Taxa table")

    occurrence_notes = models.TextField(blank=True, null=True,
                                        help_text="http://rs.tdwg.org/dwc/terms/occurrenceRemarks")
    occurrence_status = models.TextField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/iri/occurrenceStatus")
    occurrence_class = models.TextField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/terms/basisOfRecord")

    catalog_number = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="http://rs.tdwg.org/dwc/terms/catalogNumber")
    date_identified = models.DateField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/terms/dateIdentified")
    other_catalog_numbers = models.TextField(blank=True, null=True,
                                             help_text="http://rs.tdwg.org/dwc/terms/otherCatalogNumbers")
    recorded_by = models.TextField(blank=True, null=True, help_text="http://rs.tdwg.org/dwc/iri/recordedBy")

    associated_sequences = models.ManyToManyField(_("Sequences"), blank=True,
                                                  help_text="Many to many relationship with Sequence. Sequence(s) associated to this Occurrence record.")
    event = models.ForeignKey(_("Event"), related_name='occurrence', blank=True, null=True, on_delete=models.DO_NOTHING,
                              help_text="Foreign key to Event table")

    def __str__(self):
        return '{}: {}'.format(self.occurrenceID, self.taxon.name)


### End of occurrences model block
####################################################################################################
### Sample Metadata model

### This metadata table is linked to the Event (sample) - it has to be completed BEFORE creating the sample
### in order for the sample to be linked to the Metadata

class SampleMetadata(models.Model):
    metadata_tag = models.CharField(max_length=255, blank=True, null=True, default='', help_text="A tag of metadata")
    md_created_on = models.DateField(
        help_text="The date on which the resource created recommended best practice is to use an encoding scheme; such as ISO 8601:2004(E)")
    metadata_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, help_text="The user who created this record")

    license = models.CharField(max_length=100, blank=True, null=True, help_text="http://purl.org/dc/terms/license")

    geographic_location = models.ForeignKey(_("Geog_Location"), related_name='sample_metadata',
                                            on_delete=models.DO_NOTHING, blank=True, null=True,
                                            help_text="Foreign key to Geog_Location table")
    locality = models.CharField(max_length=500, blank=True, null=True,
                                help_text="http://rs.tdwg.org/dwc/terms/locality")

    geo_loc_name = models.CharField(max_length=500, blank=True, null=True,
                                    help_text="The geographical origin of the sample as defined by the country or sea name followed by specific region name. Country or sea names should be chosen from the INSDC country list (http://insdc.org/country.html); or the GAZ ontology (v 1.512) (http://purl.bioontology.org/ontology/GAZ)")  ## MIxS field

    env_biome = models.CharField(max_length=255, blank=True, null=True,
                                 help_text="Biomes are defined based on factors such as plant structures; leaf types; plant spacing; and other factors like climate. Biome should be treated as the descriptor of the broad ecological context of a sample. Examples include: desert; taiga; deciduous woodland; or coral reef. EnvO (v 2013-06-14) terms can be found via the link: www.environmentontology.org/Browse-EnvO")
    env_package = models.ForeignKey(_("package"), on_delete=models.DO_NOTHING, blank=True, null=True,
                                    help_text="Foreign key to Package table")
    env_feature = models.CharField(max_length=150, blank=True, null=True,
                                   help_text="Environmental feature level includes geographic environmental features. Compared to biome; feature is a descriptor of the more local environment. Examples include: harbor; cliff; or lake. EnvO (v 2013-06-14) terms can be found via the link: www.environmentontology.org/Browse-EnvO")
    env_material = models.CharField(max_length=150, blank=True, null=True,
                                    help_text="The environmental material level refers to the material that was displaced by the sample; or material in which a sample was embedded; prior to the sampling event. Environmental material terms are generally mass nouns. Examples include: air; soil; or water. EnvO (v 2013-06-14) terms can be found via the link: www.environmentontology.org/Browse-EnvO")

    institutionID = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="http://rs.tdwg.org/dwc/terms/institutionID")
    nucl_acid_amp = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="A link to a literature reference, electronic resource or a standard operating procedure (SOP), that describes the enzymatic amplification (PCR, TMA, NASBA) of specific nucleic acids")
    nucl_acid_ext = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="A link to a literature reference, electronic resource or a standard operating procedure (SOP), that describes the material separation to recover the nucleic acid fraction from a sample")
    ref_biomaterial = models.CharField(max_length=500, blank=True, null=True,
                                       help_text="Primary publication if isolated before genome publication; otherwise, primary genome report")
    rel_to_oxygen = models.CharField(max_length=500, blank=True, null=True,
                                     help_text="Is this organism an aerobe, anaerobe? Please note that aerobic and anaerobic are valid descriptors for microbial environments")
    rightsHolder = models.CharField(max_length=500, blank=True, null=True,
                                    help_text="http://purl.org/dc/terms/rightsHolder")
    samp_collect_device = models.CharField(max_length=500, blank=True, null=True,
                                           help_text="The method or device employed for collecting the sample")
    samp_store_dur = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True,
                                         help_text="duration for which sample was stored")
    samp_store_loc = models.CharField(max_length=500, blank=True, null=True,
                                      help_text="location at which sample was stored; usually name of a specific freezer/room")
    samp_store_temp = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True,
                                          help_text="temperature at which sample was stored, e.g. -80 degree Celsius")
    samp_vol_we_dna_ext = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True,
                                              help_text="volume (mL) or weight (g) of sample processed for DNA extraction")
    samplingProtocol = models.CharField(max_length=255, blank=True, null=True,
                                        help_text="http://rs.tdwg.org/dwc/terms/samplingProtocol")
    source_mat_id = models.CharField(max_length=500, blank=True, null=True,
                                     help_text="A unique identifier assigned to a material sample (as defined by http://rs.tdwg.org/dwc/terms/materialSampleID, and as opposed to a particular digital record of a material sample) used for extracting nucleic acids, and subsequent sequencing. The identifier can refer either to the original material collected or to any derived sub-samples. The INSDC qualifiers /specimen_voucher, /bio_material, or /culture_collection may or may not share the same value as the source_mat_id field. For instance, the /specimen_voucher qualifier and source_mat_id may both contain 'UAM:Herps:14' , referring to both the specimen voucher and sampled tissue with the same identifier. However, the /culture_collection qualifier may refer to a value from an initial culture (e.g. ATCC:11775) while source_mat_id would refer to an identifier from some derived culture from which the nucleic acids were extracted (e.g. xatc123 or ark:/2154/R2).")
    submitted_to_insdc = models.BooleanField(blank=True, null=True,
                                             help_text="Depending on the study (large-scale e.g. done with next generation sequencing technology, or small-scale) sequences have to be submitted to SRA (Sequence Read Archive), DRA (DDBJ Read Archive) or via the classical Webin/Sequin systems to Genbank, ENA and DDBJ. Although this field is mandatory, it is meant as a self-test field, therefore it is not necessary to include this field in contextual data submitted to databases")
    investigation_type = models.CharField(max_length=500, blank=True, null=True,
                                          help_text="Nucleic Acid Sequence Report is the root element of all MIGS/MIMS compliant reports as standardized by Genomic Standards Consortium. This field is either eukaryote,bacteria,virus,plasmid,organelle, metagenome,mimarks-survey, or mimarks-specimen")
    isol_growth_condt = models.CharField(max_length=255, blank=True, null=True,
                                         help_text="Publication reference in the form of pubmed ID (pmid), digital object identifier (doi) or url for isolation and growth condition specifications of the organism/material")
    lib_size = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True,
                                   help_text="Total number of clones in the library prepared for the project")

    environment = models.ManyToManyField(_("Environment"), blank=True,
                                         help_text="Environment record(s) associated to this record")

    additional_information = models.TextField(blank=True, null=True,
                                              help_text="http://rs.tdwg.org/dwc/terms/eventRemarks")

    def __str__(self):
        return self.metadata_tag or ''

    class Meta:
        verbose_name_plural = 'Metadata'


####################################################################################################


class Sequences(models.Model):
    sequence_name = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="The original sample name that can be used to identify the material taken in the field.")
    MID = models.CharField(max_length=255, blank=True, null=True,
                           help_text="Molecular barcodes, called Multiplex Identifiers (MIDs), that are used to specifically tag unique samples in a sequencing run. Sequence should be reported in uppercase letters")
    subspecf_gen_lin = models.CharField(max_length=500, blank=True, null=True,
                                        help_text="This should provide further information about the genetic distinctness of this lineage by recording additional information i.e biovar, serovar, serotype, biovar, or any relevant genetic typing schemes like Group I plasmid. It can also contain alternative taxonomic information")
    target_gene = models.CharField(max_length=500, blank=True, null=True,
                                   help_text="Targeted gene or locus name for marker gene studies")
    target_subfragment = models.CharField(max_length=500, blank=True, null=True,
                                          help_text="Name of subfragment of a gene or locus. Important to e.g. identify special regions on marker genes like V6 on 16S rRNA")
    type = models.CharField(max_length=500, blank=True, null=True,
                            help_text="The type of study; either genomic; metagenomic; transcriptomic; metatranscriptomic; viral RNA; synthetic or other.")
    primerName_forward = models.CharField(max_length=500, blank=True, null=True,
                                          help_text="http://data.ggbn.org/schemas/ggbn/terms/primerNameForward")
    primerName_reverse = models.CharField(max_length=500, blank=True, null=True,
                                          help_text="http://data.ggbn.org/schemas/ggbn/terms/primerNameReverse")
    primer_forward = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="http://data.ggbn.org/schemas/ggbn/terms/primerSequenceForward")
    primer_reverse = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="http://data.ggbn.org/schemas/ggbn/terms/primerSequenceReverse")
    run_type = models.CharField(max_length=500, blank=True, null=True,
                                help_text="The type of sequencing run performed. E.g. Illumina MiSeq 250bp paired-end")
    seqData_url = models.URLField(blank=True, null=True, help_text="relevant electronic resources")
    seqData_accessionNumber = models.CharField(max_length=500, blank=True, null=True,
                                               help_text="An associated INSDC GenBank accession number.")
    seqData_projectNumber = models.CharField(max_length=500, blank=True, null=True,
                                             help_text="An associated INSDC BioProject number.")
    seqData_runNumber = models.CharField(max_length=500, blank=True, null=True,
                                         help_text="An associated INSDC run accession number. (ERR number)")
    seqData_sampleNumber = models.CharField(max_length=500, blank=True, null=True,
                                            help_text="An associated INSDC BioSample number.")
    seqData_numberOfBases = models.BigIntegerField(blank=True, null=True,
                                                   help_text="The number of bases predicted in a sequenced sample")
    seqData_numberOfSequences = models.BigIntegerField(blank=True, null=True,
                                                       help_text="the number of sequences in a sample or folder")
    ASV_URL = models.URLField(blank=True, null=True,
                              help_text="the url to the table with Operational Taxonomic Unit (OTU) or Alternative Sequence Variants (ASV) occurrences")  ## a URL to the Alternative Sequencing Variants
    event = models.ForeignKey(_("Event"), related_name='sequences', blank=True, null=True, on_delete=models.DO_NOTHING,
                              help_text="Foreign key to Event table")

    def __str__(self):
        return self.sequence_name

    class Meta:
        ordering = ['sequence_name']
        verbose_name_plural = 'Sequences'


######################################################################################################
#### Variable and methods tables for environmental data

### These are the tables that allow you to create environmental variables, 
### units (as some variables can have the same units), 
### and methods used for collection

##### How does this translate to an excel spreadsheet?? #####

class sampling_method(models.Model):
    shortname = models.CharField(max_length=255, help_text="http://rs.tdwg.org/dwc/terms/measurementMethod")
    description = models.TextField(blank=True, null=True,
                                   help_text="a description of the sample as it was taken from the natural environment")

    def __str__(self):
        return self.shortname

    class Meta:
        ordering = ['shortname']


class units(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True,
                            help_text="the name and subject or a record (line) in a table")
    html_tag = models.CharField(max_length=200, null=True, blank=True,
                                help_text="http://rs.iobis.org/obis/terms/measurementUnitID")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Units'


class Variable(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True,
                            help_text="the name and subject or a record (line) in a table")
    var_units = models.ManyToManyField(_("units"), blank=True, help_text="Unit(s) associated with this record")
    method = models.ManyToManyField(_("sampling_method"), blank=True, help_text="Method(s) associated with this record")
    var_type = models.CharField(max_length=40, choices=(('TXT', 'Text'), ('NUM', 'Numeric')), blank=True, null=True,
                                help_text="http://rs.tdwg.org/dwc/terms/measurementType")

    def __str__(self):
        return '{} ({})'.format(self.name, self.var_type.lower())

    class Meta:
        ordering = ['name']


## We are using a manytomany relationship for method and units here because we can have multiple possible
## methods or units for any particular variable. These fields are used to populate the front end. For example
## when a user selects "sst" as their measured environmental variable, then they are forced to choose 
## the methods / units that are associated with that variable. 


#### End of environmental variable tables    
######################################################################################################
#### Environmental sample table
#### This is the table for any environmental data that are taken alongside the sequences

class Environment(models.Model):
    env_sample_name = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="The original sample name that can be used to identify the material taken in the field.")  # Uploader's personal sample ID
    created_at = models.DateField(
        help_text="The date on which the resource created recommended best practice is to use an encoding scheme; such as ISO 8601:2004(E)")

    link_climate_info = models.URLField(blank=True, null=True, help_text="link to climate resource")
    env_variable = models.ForeignKey(_("Variable"), on_delete=models.DO_NOTHING,
                                     help_text="Foreign key to Variable table")
    env_method = models.ForeignKey(_("sampling_method"), blank=True, null=True, on_delete=models.DO_NOTHING,
                                   help_text="Foreign key to sampling_method table")
    env_units = models.ForeignKey(_("units"), blank=True, null=True, on_delete=models.DO_NOTHING,
                                  help_text="Foreign key to Units table")
    ## On the front end, if env_variable.var_type is 'Text', then users input value for env_text_value
    ## if env_variable.var_type is 'Numeric', then users input value for env_numeric_value
    env_numeric_value = models.DecimalField(decimal_places=5, max_digits=25, blank=True, null=True,
                                            help_text="http://rs.tdwg.org/dwc/terms/measurementValue")
    env_text_value = models.CharField(max_length=300, blank=True, null=True,
                                      help_text="http://rs.tdwg.org/dwc/terms/measurementValue")

    event = models.ForeignKey(_("Event"), related_name='environment', blank=True, null=True,
                              on_delete=models.DO_NOTHING, help_text="Foreign key to Event table")

    def __str__(self):
        return self.env_sample_name

    class Meta:
        ordering = ['env_sample_name']
        verbose_name_plural = 'Environment samples'


#### End of environmental sample table
######################################################################################################

######################################################################################################
### Spare file table ####
class ProjectFiles(models.Model):
    files = models.FileField(upload_to=settings.POLAAAR_PROJECT_FILES_DIR, blank=True, null=True,
                             help_text="Raw data files")
    project = models.ForeignKey(_("ProjectMetadata"), blank=True, null=True, on_delete=models.CASCADE,
                                help_text="Foreign key to ProjectMetadata table")

    def __str__(self):
        return self.files.name


#####################################################################################################


### Table for mailing uploaded documents
class MailFile(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=1000)
    message = models.CharField(max_length=20000)
    # user may not be able to attach a document if the file is too big
    document = models.FileField(upload_to=settings.POLAAAR_MAIL_FILE_DIR, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # timestamp when this is first created

    def __str__(self):
        return self.email

#####################################################################################################


#### RESTRICT DATA to USER and to USER selected other users
