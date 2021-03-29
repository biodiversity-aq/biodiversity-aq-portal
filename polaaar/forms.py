from django.db.models import Count

from .models import MailFile, Variable
from django import forms
from django.core.validators import FileExtensionValidator


class EmailForm(forms.ModelForm):
    email = forms.EmailField(max_length=200, label='Your email',
                             widget=forms.TextInput(attrs={'class': "form-control", 'id': "clientemail"}))
    message = forms.CharField(label='Additional information',
                              widget=forms.Textarea(attrs={'class': "form-control"}))
    subject = forms.CharField(label='Dataset name',
                              widget=forms.TextInput(attrs={'class': "form-control"}))
    document = forms.FileField(
        required=False, widget=forms.ClearableFileInput, label='Select data file',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'tsv', 'csv', 'xls', 'xlsx', 'zip'])])

    class Meta:
        model = MailFile
        fields = ('email', 'subject', 'message', 'document',)

    def clean_document(self):
        """
        Check content type header of the file
        """
        cleaned_data = super().clean()
        data = cleaned_data.get('document')
        allowed_content_types = [
            'text/plain', 'text/csv', 'application/zip', 'application/vnd.ms-excel', 'text/tab-separated-values',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/zip']
        if data and data.content_type not in allowed_content_types:
            raise forms.ValidationError('Content type not allowed: %(value)s', code='invalid',
                                        params={'value': data.content_type})
        return data


class ProjectSearchForm(forms.Form):
    q = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "form-control form-control-sm ml-3 w-75",  "type": "text", "placeholder": "Search",
        "aria-label": "Search"}), required=False)

    def clean(self):
        cleaned_data = super(ProjectSearchForm, self).clean()
        return cleaned_data


class EnvironmentSearchForm(forms.Form):
    variable = forms.ModelChoiceField(
        queryset=Variable.objects.filter(environment__event__event_hierarchy__project_metadata__is_public=True)
            .annotate(count=Count('id')).order_by('name'),
        required=True, label='Environment variable',
        widget=forms.Select(attrs={"class": "browser-default custom-select mb-4"}))
    text = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "form-control",  "type": "text", "placeholder": "Search",
        "aria-label": "Search"}), required=False)
    min_value = forms.FloatField(required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
    max_value = forms.FloatField(required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned_data = super(EnvironmentSearchForm, self).clean()
        return cleaned_data
