### Import objects from wagtail admin
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export import resources, widgets
from import_export.fields import Field
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
#### Geog admin chunk

class GeogAdmin(ModelAdmin):
    model=Geog_Location
    menu_label = 'Geographic locations'
    menu_icon = 'site'
    menu_order = 600
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('name','geog_level','Geog_parent')
    search_fields = ('geog_level','name',
                     'parent_geog__parent_geog__name',
                     'parent_geog__parent_geog__parent_geog__name',
                     'parent_geog__parent_geog__parent_geog__parent_geog__name',
                     'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',)
    
    def Geog_parent(self,obj):
        if obj.parent_geog:
            return obj.parent_geog.geog_level+': '+obj.parent_geog.name
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
    search_fields = ('full_reference','doi','year',)
    list_display = ('full_reference','doi','year',)



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



class EventHierarchyAdmin(ModelAdmin):
    model=EventHierarchy
    menu_label='Event Hierarchy'
    menu_icon='arrow-up-big'
    menu_order = 101
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('event_creator__username','event_creator__first_name','event_creator__last_name','event_hierarchy_name')        
    list_display = ('event_hierarchy_name','description') #'Project_name',
 
    #def Project_name(self,obj):
    #    return obj.project.project_name




class EventAdmin(ModelAdmin):
    model=Event
    menu_label='Event'
    menu_icon='arrow-up'
    menu_order=102
    add_to_settings_menu=False
    exclude_from_explorer=False
    search_fields=('sample_name','parent_event__sample_name',
                   'parent_event_parent_event__sample_name')
    list_filter=('metadata_exists','occurrence_exists','environment_exists',)
    list_display=('Event_Hierarchy','sample_name','collection_year','collection_month','collection_day')

    def Event_Hierarchy(self,obj):
        return obj.event_hierarchy.event_hierarchy_name

class EventTypeAdmin(ModelAdmin):
    model=EventType
    menu_label='Event types'
    menu_icon='cog'
    menu_order=103
    add_to_settings_menu=False
    exclude_from_explorer=False


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
    model=SampleMetadata
    menu_label='Sample Metadata'
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




class pola3rAdmin(ModelAdminGroup):
    menu_label = "Pola3r"
    menu_icon = "cogs"
    menu_order = 300
    items = (MetadataAdmin,OccurrencesAdmin,SequencesAdmin,EventAdmin,EventTypeAdmin,EventHierarchyAdmin,
            ProjectMetadataAdmin,MIxSAdmin,EnvironmentalSample,SamplingVariable,SamplingUnitsAdmin,SamplingMethodAdmin,
            ReferencesAdmin,TaxaAdmin,GeogAdmin)



#########################################################################
#### Registration chunk
## This chunk registers tables to the admin so they can be manipulated through the CMS

modeladmin_register(pola3rAdmin)

##################################################################################################################################################
### Model admin for  /django-admin with import-export loading
## This chunk defines the model resources needed for the import/export package to function

class TaxaResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Taxa

class GeogResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Geog_Location

class ReferencesResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Reference

class SamplingMethodResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = sampling_method

class SamplingUnitsResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = units

class SamplingVariableResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Variable

class EnvironmentalSampleResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Environment

class MIxSResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = package

class ProjectMetadataResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = ProjectMetadata

class EventHierarchyResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = EventHierarchy


class EventResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Event

class EventTypeResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = EventType

class SequencesResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Sequences

class OccurrencesResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = Occurrence

class MetadataResource(resources.ModelResource):
    delete = Field(widget=widgets.BooleanWidget())
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)
    class Meta:
        model = SampleMetadata
    

#################################################################################################################################
#### Admin controls for IMPORT/EXPORT (found at /django-admin)

class TaxaAdminImpExp(ImportExportModelAdmin):
    resource_class = TaxaResource
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


class GeogAdminImpExp(ImportExportModelAdmin):
    resource_class = GeogResource
    list_display = ('name','geog_level','Geog_parent')
    search_fields = ('geog_level','name',
                     'parent_geog__parent_geog__name',
                     'parent_geog__parent_geog__parent_geog__name',
                     'parent_geog__parent_geog__parent_geog__parent_geog__name',
                     'parent_geog__parent_geog__parent_geog__parent_geog__parent_geog__name',)
    
    def Geog_parent(self,obj):
        if obj.parent_geog:
            return obj.parent_geog.geog_level+': '+obj.parent_geog.name
        else:
            return ''
   

class ReferenceAdminImpExp(ImportExportModelAdmin):
    resource_class = ReferencesResource
    search_fields = ('full_reference','doi','year',)
    list_display = ('full_reference','doi','year',)

class SamplingMethodAdminImpExp(ImportExportModelAdmin):
    resource_class = SamplingMethodResource
    search_fields=('shortname','description',)
    list_display=('shortname','description',)

class SamplingUnitsAdminImpExp(ImportExportModelAdmin):  
    resource_class = SamplingUnitsResource
    search_fields=('name','html_tag',)
    list_display=('name','html_tag',)


class SamplingVariableAdminImpExp(ImportExportModelAdmin):
    resource_class = SamplingVariableResource
    search_fields=('name','var_units__name','method__shortname','method__description','var_type')
    list_display=('name','var_type')

class EnvironmentalSampleAdminImpExp(ImportExportModelAdmin):
    resource_class = EnvironmentalSampleResource
    search_fields=('env_sample_name','env_variable__name','env_method__shortname',)
    list_display=('env_sample_name','created_at','varname','env_numeric_value','env_text_value')
    def varname(self,obj):
        return obj.env_variable.name

class MIxSAdminImpExp(ImportExportModelAdmin):
    resource_class = MIxSResource


class ProjectMetadataAdminImpExp(ImportExportModelAdmin):
    resource_class = ProjectMetadataResource
    search_fields=('project_name','abstract','project_creator__username','project_creator__first_name','project_creator__last_name')
    list_filter = ('is_public','project_qaqc')    
    list_display = ('project_name','start_date','end_date','is_public','abstract','project_qaqc')


class EventHierarchyAdminImpExp(ImportExportModelAdmin):
    resource_class = EventHierarchyResource
    search_fields=('event_creator__username','event_creator__first_name','event_creator__last_name','event_hierarchy_name')        
    list_display = ('event_hierarchy_name','description')#'Project_name',
 
    #def Project_name(self,obj):
    #    return obj.project.project_name

class EventAdminImpExp(ImportExportModelAdmin):
    resource_class = EventResource
    search_fields=('sample_name','parent_event__sample_name',
                   'parent_event_parent_event__sample_name')
    list_filter=('metadata_exists','occurrence_exists','environment_exists',)
    list_display=('Event_Hierarchy','sample_name','collection_year','collection_month','collection_day')

    def Event_Hierarchy(self,obj):
        return obj.event_hierarchy.event_hierarchy_name

class EventTypeAdminImpExp(ImportExportModelAdmin):
    resource_class = EventTypeResource


class SequencesAdminImpExp(ImportExportModelAdmin):
    resource_class = SequencesResource
    search_fields=('sequence_name','MID','target_gene','seqData_url',
                   'subspecf_gen_lin','seqData_accessionNumber','seqData_projectNumber',
                   'seqData_runNumber','seqData_sampleNumber','seqData_numberOfBases')
    list_display=('sequence_name','MID','target_gene','seqData_url',
                   'subspecf_gen_lin','seqData_accessionNumber','seqData_projectNumber',
                   'seqData_runNumber','seqData_sampleNumber','seqData_numberOfBases')

class OcurrencesAdminImpExp(ImportExportModelAdmin):
    resource_class = OccurrencesResource
    search_fields = ('occurrenceID','taxon__name','occurrence_class','catalog_number',
                     'occurrence_status','recorded_by')
    list_display = ('occurrenceID','taxonname','occurrence_class','catalog_number',
                     'occurrence_status','recorded_by','date_identified')

    def taxonname(self,obj):
        return obj.taxon.name

class MetadataResourceAdminImpExp(ImportExportModelAdmin):
    resource_class = MetadataResource
    search_fields=('metadata_tag','metadata_creator__username','metadata_creator__first_name',
                   'metadata_creator__last_name','continent','country.name','waterBody',
                   'islandGroup','island','location','geo_loc_name')

    list_display = ('metadata_tag','name','md_created_on')


    def name(self,obj):
        return obj.metadata_creator.first_name+' '+obj.metadata_creator.first_name

#########################################################################################################################################################
#### Register admin

admin.site.register(Taxa,TaxaAdminImpExp)
admin.site.register(Geog_Location,GeogAdminImpExp)
admin.site.register(Reference,ReferenceAdminImpExp)
admin.site.register(sampling_method,SamplingMethodAdminImpExp)
admin.site.register(units,SamplingUnitsAdminImpExp)
admin.site.register(Variable,SamplingVariableAdminImpExp)
admin.site.register(Environment,EnvironmentalSampleAdminImpExp)
admin.site.register(package,MIxSAdminImpExp)
admin.site.register(ProjectMetadata,ProjectMetadataAdminImpExp)
admin.site.register(EventHierarchy,EventHierarchyAdminImpExp)
admin.site.register(Event,EventAdminImpExp)
admin.site.register(EventType,EventTypeAdminImpExp)
admin.site.register(Sequences,SequencesAdminImpExp)
admin.site.register(Occurrence,OcurrencesAdminImpExp)
admin.site.register(SampleMetadata,MetadataResourceAdminImpExp)
