from __future__ import unicode_literals


from django.db import models
from django.contrib import admin
from django.utils.translation import gettext as _
from django.utils.html import format_html
from django.conf import settings
from django.contrib.gis.gdal import *
#from djgeojson.fields import PointField
from django.contrib.gis.db import models

from django_countries.fields import CountryField
from django.core.files.storage import FileSystemStorage




### Hard-wiring in choices for continent 
CONTINENTS = [
    ('NA','North America'),
    ('SA','South America'),
    ('EU','Europe'),
    ('OC','Oceania'),
    ('AN','Antarctica'),
    ('AS','Asia'),
    ('AF','Africa')
    ]


############################################################################################
#### Taxonomy model block

## This block defines the db table (model) for the taxonomy.
## We have opted to do this as a recursive table which is an efficient way to handle non-specific
## endpoints. This way, the data can be linked at any taxa level.

TAXA = (
    ('superKingdom','superKingdom'),
    ('Kingdom','Kingdom'),
    ('SubKingdom','SubKingdom'),
    ('Phylum','Phylum'),
    ('SubPhylum','SubPhylum'),
    ('Class','Class'),
    ('SubClass','SubClass'),
    ('Order','Order'),
    ('SubOrder','SubOrder'),
    ('Family','Family'),
    ('SubFamily','SubFamily'),
    ('Genus','Genus'),
    ('SubGenus','SubGenus'),
    ('Species','Species'),
    ('SubSpecies','SubSpecies'),
    ('Strain','Strain')
    )

class Taxa(models.Model):
    name            = models.CharField(max_length=255,null=True,blank=True)
    TaxonRank       = models.CharField(max_length=100,choices=TAXA,blank=True,null=True)
    taxonID         = models.CharField(max_length=100,blank=True,null=True) ## From WORMS
    ## this is the recursive link to the table. We allow this to be null and blank
    ## because at the top level (Kingdom), we wouldn't have a parent
    parent_taxa     = models.ForeignKey('self',on_delete=models.DO_NOTHING,related_name='TaxonName',blank=True,null=True)

    ### Add constraint to not point to its own rank :) 


    def __str__(self):
        return self.TaxonRank +': '+ self.name
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

#BIOME_LEVELS = (
#    ('L1',"Level_1"),
#    ('L2',"Level_2"),
#    ('L3',"Level_3"),
#    ('L4',"Level_4"),
#    ('L5',"Level_5")
#    )


#class Biome(models.Model):
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
    ('Conti','Continent'),
    ('Count','Country'),
    ('Sta','State'),
    ('Prov','Province'),
    ('IslG','Island_Group'),
    ('Isl','Island'),
    ('Pla','Place_Name'),
    ('Ocean','Ocean'),
    ('Sea','Sea'),
    ('Bay','Bay'),
    ('Wb','Water_body')
)

class Geog_Location(models.Model):
    name            = models.CharField(max_length=300,null=True,blank=True)
    geog_level      = models.CharField(max_length=300,choices=GEOG_LEVELS)
    parent_geog     = models.ForeignKey('self',on_delete=models.DO_NOTHING,related_name='GeogName',blank=True,null=True)

    def __str__(self):
        return self.geog_level+': '+self.name  
    class Meta:
        ordering=['name']




#####################################################################################################
#### MIxS package table

class package(models.Model):
    name                = models.CharField(max_length=255,null=True,blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering=['name']

##### End of MIxS package model block
#####################################################################################################
#### References tables

### This is a simple references table. We have kept this simple here because there will be generally low
### volumes of data coming in, and therefore it can easily be cleaned if need be. 

class Reference(models.Model):
    full_reference  = models.TextField()                         ### The full reference 
    doi             = models.CharField(max_length=255,blank=True,null=True) ### doi of the reference if known
    #short_authors = models.CharField(max_length=150)            ### Short authors list. e.g., Humphries et al. / Humphries and van de Putte
    #journal = models.TextField()                                ### The journal or the book that the reference is in
    year            = models.IntegerField()                      ### The year the reference was published

    #occurrences = models.ManyToManyField(_("Occurrence"),blank=True)

    def __str__(self):
        return self.full_reference
    class Meta:
        ordering = ['-year']                                    ### Order this by year (descending), listing most recent first

##### End of References models block
#####################################################################################################



######################################################################################################
### ParentEvents tables
# The ParentEvent table defines the broad parameters from which the samples were taken. This is done via another
# recursive model, allowing the user to define the hierarchy of the sampling. 
# For example, a top level parentevent could be a project, next a cruise, then a transect. 

## We're not sure what kind of events we could have, so we'll create a table to make it easy to add these
class EventType(models.Model):
    name                             = models.CharField(max_length=255,null=True,blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class ProjectMetadata(models.Model):
    project_name                    = models.CharField(max_length=255)
    start_date                      = models.DateField()
    end_date                        = models.DateField(blank=True,null=True)
    EML_URL                         = models.URLField(blank=True,null=True)            ## URL to GBIF generated EML file
    abstract                        = models.TextField(blank=True,null=True)           ## Abstract for the event, if available
    
    geomet                          = models.PolygonField(srid=4326, blank=True, null=True)
    
    is_public                       = models.BooleanField()
    associated_references           = models.ForeignKey(_("Reference"),blank=True,null=True,on_delete=models.DO_NOTHING)
    associated_media                = models.TextField(blank=True,null=True)
    created_on                      = models.DateField()
    updated_on                      = models.DateField(auto_now=True)

    project_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    project_qaqc                    = models.BooleanField(blank=True,null=True)

    def __str__(self):
        return self.project_name
    class Meta:
        ordering = ['project_name']

####################################################################################################################

## Add table here for lost datasets / data with no structure?
####################################################################################################################

################################################################################
### Change event type to TextField?
################################################################################


## Change to EventHierarchy

class EventHierarchy(models.Model):
    parent_event_name               = models.CharField(max_length=255)                        ## User's project name or cruise name, etc...
    event_type                      = models.ForeignKey(_("EventType"),
                                                            on_delete=models.DO_NOTHING)  ## Drawn from the Event_type table
       
    description                     = models.TextField()                                            ## Description of the event
    
    parent_event                    = models.ForeignKey('self',on_delete=models.DO_NOTHING,related_name='EventRank',blank=True,null=True)
    event_creator                   = models.ForeignKey(
                                        settings.AUTH_USER_MODEL,
                                        on_delete=models.CASCADE)
    created_on                      = models.DateField()
    updated_on                      = models.DateField(auto_now=True)
    
    project_metadata                = models.ForeignKey(_("ProjectMetadata"),blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.event_type.name +': '+ self.parent_event_name
    class Meta:
        ordering=['parent_event_name']

#### End of parent event models block
####################################################################################################
### Event table block 

## This table refers to specific samples taken, and is recursive - so if a sample gets SUBSAMPLED
## then a new event (sample) can be defined with the original sample as a parent.

class Event(models.Model):

    footprintWKT        = models.GeometryField(srid=4326,blank=True,null=True)
    
    Latitude            = models.DecimalField(decimal_places=5,max_digits=10,blank=True,null=True) 
    Longitude           = models.DecimalField(decimal_places=5,max_digits=10,blank=True,null=True)

    eventRemarks        = models.TextField(blank=True,null=True)
    sample_name         = models.CharField(max_length=255,unique=True)   ### Unique value      ## User provided id for sample
    collection_date     = models.DateField()
    collection_time     = models.TimeField()
    parent_event        = models.ForeignKey(_("EventHierarchy"),on_delete=models.CASCADE)
    ### Sample is a recursive table, and can be sub-sampled    
    parent_sample       = models.ForeignKey('self',
                                      on_delete=models.DO_NOTHING,
                                      blank=True,
                                      null=True)
    
    samplingProtocol    = models.TextField(blank=True,null=True)

    occurrence          = models.ManyToManyField(_("Occurrence"),blank=True)    
    environment         = models.ManyToManyField(_("Environment"),blank=True)

    metadata_exists     = models.BooleanField(blank=True,null=True)
    occurrence_exists   = models.BooleanField(blank=True,null=True)
    environment_exists  = models.BooleanField(blank=True,null=True)
    

    def __str__(self):
        return self.parent_event.parent_event_name +', '+ self.sample_name
    class Meta:
        ordering = ['-collection_date','-collection_time']

#### End of event models block        
####################################################################################################
### Occurrences block

### This is a table which records any occurrences associated with a sample. 
class Occurrence(models.Model):
    occurrenceID            = models.CharField(max_length=255,blank=True,null=True)
    taxon                   = models.ForeignKey(_('Taxa'),on_delete=models.DO_NOTHING)

    occurrence_notes        = models.TextField(blank=True,null=True)
    occurrence_status       = models.TextField(blank=True,null=True)
    occurrence_class        = models.TextField(blank=True,null=True)
    
    catalog_number          = models.CharField(max_length=255,blank=True,null=True)
    date_identified         = models.DateField(blank=True,null=True)
    other_catalog_numbers   = models.TextField(blank=True,null=True)
    recorded_by             = models.TextField(blank=True,null=True)

    associated_sequences    = models.ManyToManyField(_("Sequences"),blank=True)

    def __str__(self):
        return self.occurrenceID + ': ' + self.taxon.name
### End of occurrences model block
####################################################################################################
### Metadata model

### This metadata table is linked to the Event (sample) - it has to be completed BEFORE creating the sample
### in order for the sample to be linked to the Metadata

class Metadata(models.Model):  ### rename to Sample_metadata
    metadata_tag            = models.CharField(max_length=255,blank=True,null=True)
    md_created_on           = models.DateField()
    metadata_creator        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    
    license                 = models.CharField(max_length=100,blank=True,null=True)
    
    geographic_location     = models.ForeignKey(_("Geog_Location"),on_delete=models.DO_NOTHING,blank=True,null=True)
    locality                = models.CharField(max_length=50,blank=True,null=True)
    
    geo_loc_name            = models.CharField(max_length=50,blank=True,null=True)                 ## MIxS field
       
    env_biome               = models.CharField(max_length=255,blank=True,null=True)  
    env_package             = models.ForeignKey(_("package"),on_delete=models.DO_NOTHING,blank=True,null=True)
    env_feature             = models.CharField(max_length=50,blank=True,null=True)
    env_material            = models.CharField(max_length=50,blank=True,null=True)
    
    institutionID           = models.CharField(max_length=255,blank=True,null=True)
    nucl_acid_amp           = models.CharField(max_length=255,blank=True,null=True)
    nucl_acid_ext           = models.CharField(max_length=255,blank=True,null=True)
    ref_biomaterial         = models.CharField(max_length=50,blank=True,null=True)
    rel_to_oxygen           = models.CharField(max_length=50,blank=True,null=True)
    rightsHolder            = models.CharField(max_length=50,blank=True,null=True)
    samp_collect_device     = models.CharField(max_length=50,blank=True,null=True)
    samp_store_dur          = models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    samp_store_loc          = models.CharField(max_length=50,blank=True,null=True)
    samp_store_temp         = models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    samp_vol_we_dna_ext     = models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    samplingProtocol        = models.CharField(max_length=255,blank=True,null=True)
    source_mat_id           = models.CharField(max_length=50,blank=True,null=True)
    submitted_to_insdc      = models.BooleanField(blank=True,null=True)
    investigation_type      = models.CharField(max_length=50,blank=True,null=True)
    isol_growth_condt       = models.CharField(max_length=255,blank=True,null=True)
    lib_size                = models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True )

    sequence                = models.ManyToManyField(_("Sequences"),blank=True)

    additional_information  = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return self.metadata_tag

    class Meta:
        verbose_name_plural = 'Metadata'


####################################################################################################


class Sequences(models.Model):
    sequence_name               = models.CharField(max_length=255)    
    MID                         = models.CharField(max_length=255,blank=True,null=True)
    subspecf_gen_lin            = models.CharField(max_length=50,blank=True,null=True)
    target_gene                 = models.CharField(max_length=50,blank=True,null=True)
    target_subfragment          = models.CharField(max_length=50,blank=True,null=True)
    type                        = models.CharField(max_length=50,blank=True,null=True)
    primerName_forward          = models.CharField(max_length=50,blank=True,null=True)
    primerName_reverse          = models.CharField(max_length=50,blank=True,null=True)
    primer_forward              = models.CharField(max_length=255,blank=True,null=True)
    primer_reverse              = models.CharField(max_length=255,blank=True,null=True)
    run_type                    = models.CharField(max_length=50,blank=True,null=True)
    seqData_url                 = models.URLField(blank=True,null=True)
    seqData_accessionNumber     = models.CharField(max_length=50,blank=True,null=True)
    seqData_projectNumber       = models.CharField(max_length=50,blank=True,null=True)
    seqData_runNumber           = models.CharField(max_length=50,blank=True,null=True)
    seqData_sampleNumber        = models.CharField(max_length=50,blank=True,null=True)
    seqData_numberOfBases       = models.IntegerField(blank=True,null=True)
    seqData_numberOfSequences   = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return self.sequence_name
    class Meta:
        ordering=['sequence_name']
        verbose_name_plural = 'Sequences'


######################################################################################################
#### Variable and methods tables for environmental data

### These are the tables that allow you to create environmental variables, 
### units (as some variables can have the same units), 
### and methods used for collection

##### How does this translate to an excel spreadsheet?? #####

class sampling_method(models.Model):
    shortname                   = models.CharField(max_length=255)
    description                 = models.TextField(blank=True,null=True)
    def __str__(self):
        return self.shortname
    class Meta:
       ordering = ['shortname']


class units(models.Model):    
    name                        = models.CharField(max_length=255,null=True,blank=True)
    html_tag                    = models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Units'

class Variable(models.Model):
    name                        = models.CharField(max_length=100,null=True,blank=True)
    var_units                   = models.ManyToManyField(_("units"),blank=True)             
    method                      = models.ManyToManyField(_("sampling_method"),blank=True)
    var_type                    = models.CharField(max_length=40,choices=(('TXT','Text'),('NUM','Numeric')),blank=True,null=True)

    def __str__(self):
        return self.name
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
    env_sample_name             = models.CharField(max_length=255,blank=True,null=True)   # Uploader's personal sample ID
    created_at                  = models.DateField()
         
    link_climate_info           = models.URLField(blank=True,null=True)
    env_variable                = models.ForeignKey(_("Variable"),on_delete=models.DO_NOTHING)
    env_method                  = models.ForeignKey(_("sampling_method"),blank=True,null=True,on_delete=models.DO_NOTHING)
    env_units                   = models.ForeignKey(_("units"),blank=True,null=True,on_delete=models.DO_NOTHING)
    
    sequences                   = models.ManyToManyField(_("Sequences"),blank=True)
    
    ## On the front end, if env_variable.var_type is 'Text', then users input value for env_text_value
    ## if env_variable.var_type is 'Numeric', then users input value for env_numeric_value
    env_numeric_value           = models.DecimalField(decimal_places=5,max_digits=15,blank=True,null=True)
    env_text_value              = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.env_sample_name
    class Meta:
        ordering = ['env_sample_name']
        verbose_name_plural = 'Environment samples'
       
#### End of environmental sample table
######################################################################################################

######################################################################################################
####
### Spare file table ####
fs = FileSystemStorage(location='/media/files')
class HomelessFiles(models.Model):
    files                       = models.FileField(storage=fs,blank=True,null=True)
    event                       = models.ForeignKey(_("Event"),on_delete=models.CASCADE)

#####################################################################################################

    
### Table for mailing uploaded documents
class MailFile(models.Model):
    email                       = models.EmailField() 
    subject                     = models.CharField(max_length=1000)
    message                     = models.CharField(max_length=20000)
    document                    = models.FileField(upload_to='uploads/')
    def __str__(self):
        return self.email




#####################################################################################################
#class Amplicon(models.Model):
#    AmpImg = models.ImageField()
    


#### RESTRICT DATA to USER and to USER selected other users
