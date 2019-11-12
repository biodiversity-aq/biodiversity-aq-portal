# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template import defaultfilters
from django.forms.widgets import CheckboxSelectMultiple


from crispy_forms.bootstrap import InlineField,InlineCheckboxes, StrictButton,InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, ButtonHolder,HTML

from ..core.conf import settings
from ..core.utils.timezone import timezones
from .models import UserProfile




User = get_user_model()
TIMEZONE_CHOICES = timezones()


class CleanEmailMixin(object):

    def clean_email(self):
        email = self.cleaned_data["email"]

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            email = email.lower()

        if not settings.ST_UNIQUE_EMAILS:
            return email

        is_taken = (
            User.objects
            .filter(email=email)
            .exists())

        if is_taken:
            raise forms.ValidationError(_("The email is taken."))

        return email

    def get_email(self):
        return self.cleaned_data["email"]


class EmailCheckForm(CleanEmailMixin, forms.Form):

    email = forms.CharField(label=_("Email"), widget=forms.EmailInput, max_length=254)


class EmailChangeForm(CleanEmailMixin, forms.Form):

    email = forms.CharField(label=_("Email"), widget=forms.EmailInput, max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]

        if not self.user.check_password(password):
            raise forms.ValidationError(_("The provided password is incorrect."))

        return password


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("first_name", "last_name")

    def __init__(self, *args, **kwargs):                  
        super(UserForm, self).__init__(*args, **kwargs)
        self.user = kwargs.pop('instance')
        self.helper = FormHelper(self)
        self.initial['first_name'] = self.user.first_name
        self.initial['last_name'] = self.user.last_name
        self.helper.layout = Layout(
            Row(Column('first_name',css_class='form-group col-sm-6'),
                Column('last_name',css_class='form-group col-sm-6'))            
            )


class UserProfileForm(forms.ModelForm):
    
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = UserProfile       
        fields = ("first_name","last_name","institution","introduction",
                  "resident_country","home_country",                
                  "position","gdpr","email_contact")
        labels = {
            
            "gdpr": _("Do you give consent for biodiversity.aq to store your personal data? We will never use it for commercial purposes or sell it to any third party (required)"),
            "resident_country": _("Country of current residence (optional)"),
            "home_country": _("Home country (optional)"),

            "introduction":_("Write a short introduction for yourself describing why you're here (max 1500 characters)"),           
            
            "email_contact":_("Is it okay for us to send you an e-mail once in a while with updates or news? (This happens very infrequently)")            
        }


    def __init__(self, *args, **kwargs):
          
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        #terms_and_conditions = reverse_lazy("terms_and_conditions")
        user = kwargs.pop('instance')
        
        username = user.nickname        

        self.initial['first_name'] = user.user.first_name
        self.initial['last_name'] = user.user.last_name
       
        self.fields['gdpr'].label = mark_safe(_("Do you consent to Biodiversity.aq storing your personal data? Please read the "
                                                      "<a target='_blank' href='/privacy-policy'>Terms and Conditions</a> <strong>(Required)</strong>")) #% (terms_and_conditions)
        self.helper.layout = Layout(
            
            Row(Column('first_name',css_class='form-group col-sm-6'),
                Column('last_name',css_class='form-group col-sm-6')
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
            ButtonHolder(
                Submit("submit", "Save",css_class="buttonsave")
            )
                                                                      
            )
        