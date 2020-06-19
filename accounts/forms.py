from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile
from django.utils.safestring import mark_safe
from django.db import models

from crispy_forms.bootstrap import InlineField,InlineCheckboxes, StrictButton,InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, ButtonHolder,HTML
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from django_countries.fields import CountryField

BOOLEAN_YN = (
(True, u'Yes'),
(False, u'No'),  
)

     
class CustomUserCreationForm(UserCreationForm):  

    #email2 = forms.CharField(
    #    label=_("Email confirmation"),
    #    widget=forms.EmailInput,
    #    max_length=254,
    #    help_text=_("Enter the same email as above, for verification."))

    honeypot = forms.CharField(
        label=_("Leave blank"),
        required=False)


    def clean_honeypot(self):
        """Check that nothing has been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]

        if value:
            raise forms.ValidationError(
                _("CAUGHT YOU, you nasty bot..."))

        return value


    #def clean_email2(self):
    #    email = self.cleaned_data.get("email")
    #    email2 = self.cleaned_data["email2"]

    #    if settings.ST_CASE_INSENSITIVE_EMAILS:
    #        email2 = email2.lower()

    #    if email and email != email2:
    #        raise forms.ValidationError(
    #            _("The two email fields didn't match."))

    #    return email2


    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'last_name','email','password1','password2',
                  'position','institution','resident_country','home_country','introduction','gdpr','email_contact')
        labels = {
            
            "gdpr": _("Do you give consent for biodiversity.aq to store your personal data? We will never use it for commercial purposes or sell it to any third party (required)"),
            "resident_country": _("Country of current residence (optional)"),
            "home_country": _("Home country (optional)"),

            "introduction":_("Why are you using our site? (max 1500 characters)"),           
            
            "email_contact":_("Is it okay for us to send you an e-mail once in a while with updates or news? (This happens very infrequently)")            
        }

    # Add this to check if both passwords are matching or not

       

    def clean(self):
        cleaned_data = super(CustomUserCreationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Passwords do not match!')
    # Add this to check if the email already exists in your database or not
    
    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if email and UserProfile.objects.filter(email=email).exclude(username=username).count():          
            raise forms.ValidationError('This email is already in use! Try another email.')
        return email
    
    ## Add this to check if the username already exists in your database or not
    def clean_username(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if username and UserProfile.objects.filter(username=username).exclude(email=email).count():
            raise forms.ValidationError('This username has already been taken!')
        return username


    def __init__(self, *args, **kwargs):
          
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        #terms_and_conditions = reverse_lazy("terms_and_conditions")
        #user = kwargs.pop('instance')
            
        #self.fields['gdpr'].label = mark_safe(_("Do you consent to Biodiversity.aq storing your personal data? Please read the <a target='_blank' href='/privacy-policy'>Terms and Conditions</a> <strong>(Required)</strong>")) #% (terms_and_conditions)
        self.helper.layout = Layout(
            
      
            Row(Column('username',css_class='form-group col-sm-4'),
                Column('first_name',css_class='form-group col-sm-4'),
                Column('last_name',css_class='form-group col-sm-4'),
                Column('email',css_class='form-group col-sm-12'),
                Column('password1',css_class='form-group col-sm-6'),
                Column('password2',css_class='form-group col-sm-6'),
            ),
            Row(InlineRadios('gdpr')),
            Row(InlineRadios('email_contact')),
            Row(                
                Column('position',css_class='form-group col-md-6'),
                Column('institution',css_class='form-group col-md-6'),                
                ),
            Row(
                Column('introduction',css_class='form-group col-md-12'),                
                Column('resident_country',css_class='form-group col-md-6'),
                Column('home_country',css_class='form-group col-md-6'),                       
                ),
            HTML('<script src="https://www.google.com/recaptcha/api.js"></script>'),
            HTML('<div class="g-recaptcha" data-sitekey="{}"></div>'.format(settings.RECAPTCHA_SITE_KEY)),
            ButtonHolder(
                Submit("submit", "Register",css_class="btn btn-deep-orange btn-lg")
            )                                                       
            )

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = UserProfile
        fields = ('username', 'email')