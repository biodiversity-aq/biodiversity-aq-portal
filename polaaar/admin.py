### Import objects from wagtail admin
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from django.contrib import admin
# Import models from the app, polarrr  (.models means to get the models.py in the same directory as this file)
from .models import *
# Register your models here.

###################################################################################
### Taxonomic table admin registration for wagtail (ModelAdmin) and django-admin

class TaxaAdmin(ModelAdmin):
    model=Taxa                                              ## Selects which model to work with
    menu_label='Taxonomy'                                   ## Sets what will be displayed in the CMS
    menu_icon='wagtail'                                     ## Sets the icon that will be displayed
    menu_order=500                                          ## Determines where on the CMS menu it will appear
    add_to_settings_menu=False                              ## if true, the model will appear in the 'settings' menu
    exclude_from_explorer=False                             ## if true, won't be displayed 
    list_display=('TaxonRank','name','Taxonomic_parent')    ## Like django admin options, displays data as a table
    search_fields = ('TaxonRank','name',                    ## These are the fields that we can search by. 
                     'parent_taxa__name',                   ## Because this table is recursive, we repeat this and add 
                     'parent_taxa__parent_taxa__name',      ## the value "parent_taxa" at each stage to tell it to search further down the tree
                     'parent_taxa__parent_taxa__parent_taxa__name',
                     'parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
                     'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
                     'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',
                     'parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__parent_taxa__name',)

    ### These functions and those like it, are used for the list_display option, which requires it.
    ### It will return the name of the parent taxon in the form:  Kindom:Bacteria  
    def Taxonomic_parent(self,obj):
        if obj.parent_taxa:
            return obj.parent_taxa.TaxonRank+':'+obj.parent_taxa.name
        else:
            return ''


##############################################################################################################################
#### Biome admin chunk
class BiomeAdmin(ModelAdmin):
    model=Biome
    menu_label = 'Biomes'
    menu_icon = 'snippet'
    menu_order = 600
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('name','biome_level','Biome_parent')
    search_fields = ('biome_level','name',
                     'parent_biome__parent_biome__name',
                     'parent_biome__parent_biome__parent_biome__name',
                     'parent_biome__parent_biome__parent_biome__parent_biome__name',
                     'parent_biome__parent_biome__parent_biome__parent_biome__parent_biome__name',)
    
    def Biome_parent(self,obj):
        if obj.parent_biome:
            return obj.parent_biome.biome_level+': '+obj.parent_biome.name
        else:
            return ''


        
##############################################################################################################################
### References Admin 
class ReferencesAdmin(ModelAdmin):
    model=Reference
    menu_label = 'References'
    menu_icon = 'list-ul'
    menu_order = 450
    add_to_settings_menu = False
    exclude_from_explorer = False
    search_fields = ('title','short_authors','year','journal','doi','authors_list',)
    list_display = ('title','short_authors','year','journal','doi','authors_list',)



##############################################################################################################################
### Environmental data Admin 
class SamplingMethodAdmin(ModelAdmin):
    model=sampling_method
    menu_label='Sampling methods'
    menu_icon = 'plus'
    menu_order = 100
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('shortname','description',)
    list_display=('shortname','description',)

class SamplingUnitsAdmin(ModelAdmin):
    model=units
    menu_label='Environmental Sampling units'
    menu_icon = 'plus'
    menu_order = 101
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('name','html_tag',)
    list_display=('name','html_tag',)

class SamplingVariable(ModelAdmin):
    model=Variable
    menu_label='Environmental sampling variables'
    menu_icon='plus'
    menu_order = 102
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('name','var_units__name','method__shortname','method__description','var_type')
    list_display=('name','var_type')
    #list_filter=('var_type')

class EnvironmentalSample(ModelAdmin):
    model=Environment
    menu_label='Environmental samples'
    menu_icon='table'
    menu_order = 103
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('env_sample_name','env_variable__name','env_method__shortname',)
    list_display=('env_sample_name','created_at','varname','env_numeric_value','env_text_value')
#   list_filter=('var_type')

    def varname(self,obj):
        return obj.env_variable.name

class MIxSAdmin(ModelAdmin):
    model=package
    menu_label='MIxS packages'
    menu_icon='cogs'
    menu_order = 104
    add_to_settings_menu=False
    exclude_from_explorer=False
    

class EnvironmentGroup(ModelAdminGroup):
    menu_label = "Environmental"
    menu_icon = "snippet"
    menu_order = 502
    items = (SamplingMethodAdmin,SamplingUnitsAdmin,SamplingVariable,EnvironmentalSample,MIxSAdmin)



##############################################################################################################################
### Parent event and event models


class ProjectMetadataAdmin(ModelAdmin):
    model=ProjectMetadata
    menu_label='Project metadata'
    menu_icon='arrow-up-big'
    menu_order = 100
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('project_name','abstract','project_creator__username','project_creator__first_name','project_creator__last_name')
    list_filter = ('is_public','project_qaqc')    
    list_display = ('project_name','start_date','end_date','is_public','abstract','project_qaqc')



class ParentEventAdmin(ModelAdmin):
    model=ParentEvent
    menu_label='Parent Event'
    menu_icon='arrow-up-big'
    menu_order = 101
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('event_creator__username','event_creator__first_name','event_creator__last_name','event_name')        
    list_display = ('Project_name','event_name','description')
 
    def Project_name(self,obj):
        return obj.project.project_name




class EventAdmin(ModelAdmin):
    model=Event
    menu_label='Event'
    menu_icon='arrow-up'
    menu_order=102
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('sample_name','parent_sample__sample_name',
                   'parent_sample_parent_sample__sample_name')
    list_filter=('metadata_exists','occurrence_exists','environment_exists',)
    list_display=('Parent_Event','sample_name','collection_date')

    def Parent_Event(self,obj):
        return obj.parent_event.event_name

class EventTypeAdmin(ModelAdmin):
    model=EventType
    menu_label='Event types'
    menu_icon='cog'
    menu_order=103
    add_to_settings_menu=False
    exclude_from_explorer=False

class EventGroup(ModelAdminGroup):
    menu_label = "Events"
    menu_icon = "arrows-up-down"
    menu_order = 503
    items = (ProjectMetadataAdmin,ParentEventAdmin,EventAdmin,EventTypeAdmin)

### End of event model admin
#########################################################################################
### Sequences admin

class SequencesAdmin(ModelAdmin):
    model=Sequences
    menu_label='Sequences'
    menu_icon='list-ul'
    menu_order = 505
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('sequence_name','MID','target_gene','seqData_url',
                   'subspecf_gen_lin','seqData_accessionNumber','seqData_projectNumber',
                   'seqData_runNumber','seqData_sampleNumber','seqData_numberOfBases')
    list_display=('sequence_name','MID','target_gene','seqData_url',
                   'subspecf_gen_lin','seqData_accessionNumber','seqData_projectNumber',
                   'seqData_runNumber','seqData_sampleNumber','seqData_numberOfBases')
### End of sequences admin block    
########################################################################################
### Occurrences model admin

class OccurrencesAdmin(ModelAdmin):
    model=Occurrence
    menu_label='Occurrences'
    menu_icon='site'
    menu_order = 506
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields = ('occurrenceID','taxon__name','occurrence_class','catalog_number',
                     'occurrence_status','recorded_by')
    list_display = ('occurrenceID','taxonname','occurrence_class','catalog_number',
                     'occurrence_status','recorded_by','date_identified')

    def taxonname(self,obj):
        return obj.taxon.name

    
#########################################################################################

class MetadataAdmin(ModelAdmin):
    model=Metadata
    menu_label='Metadata'
    menu_icon='doc-full'
    menu_order = 507
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('metadata_tag','metadata_creator__username','metadata_creator__first_name',
                   'metadata_creator__last_name','continent','country.name','waterBody',
                   'islandGroup','island','location','geo_loc_name')

    list_display = ('metadata_tag','name','md_created_on')


    def name(self,obj):
        return obj.metadata_creator.first_name+' '+obj.metadata_creator.first_name





#########################################################################
#### Registration chunk
## This chunk registers tables to the admin so they can be manipulated through the CMS
modeladmin_register(ReferencesAdmin)
modeladmin_register(TaxaAdmin)
modeladmin_register(EnvironmentGroup)
modeladmin_register(BiomeAdmin)
modeladmin_register(EventGroup)
modeladmin_register(SequencesAdmin)
modeladmin_register(OccurrencesAdmin)
modeladmin_register(MetadataAdmin)


