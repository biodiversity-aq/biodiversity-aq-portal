from .models import MailFile
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
        required=True, widget=forms.ClearableFileInput, label='Select data file',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'tsv', 'csv', 'xls', 'xlsx', 'zip'])])

    class Meta:
        model = MailFile
        fields = ('email', 'subject', 'message', 'document',)
