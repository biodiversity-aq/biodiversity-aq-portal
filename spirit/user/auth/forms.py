# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext, gettext_lazy as _



from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.text import capfirst
from django.template import loader



from post_office import mail as pomail
from post_office.models import EmailTemplate


from ...core.conf import settings
from ..forms import CleanEmailMixin

User = get_user_model()


class RegistrationForm(CleanEmailMixin, forms.ModelForm):

    email2 = forms.CharField(
        label=_("Email confirmation"),
        widget=forms.EmailInput,
        max_length=254,
        help_text=_("Enter the same email as above, for verification."))
    # todo: add password validator for Django 1.9
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput)
    honeypot = forms.CharField(
        label=_("Leave blank"),
        required=False)

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True  # Django model does not requires it

    def clean_honeypot(self):
        """Check that nothing has been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]

        if value:
            raise forms.ValidationError(
                _("Do not fill this field."))

        return value

    def clean_username(self):
        username = self.cleaned_data["username"]

        if settings.ST_CASE_INSENSITIVE_USERNAMES:
            username = username.lower()

        is_taken = (
            User.objects
            .filter(username=username)
            .exists())
        if is_taken:
            raise forms.ValidationError(
                _("The username is taken."))

        return self.cleaned_data["username"]

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data["email2"]

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            email2 = email2.lower()

        if email and email != email2:
            raise forms.ValidationError(
                _("The two email fields didn't match."))

        return email2

    def save(self, commit=True):
        self.instance.is_active = False
        self.instance.set_password(self.cleaned_data["password"])
        return super(RegistrationForm, self).save(commit)


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label=_("Username or Email"),
        max_length=254)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = _("The password is not valid.")

    def _validate_username(self):
        """
        Check the username exists.\
        Show if the username or email is invalid\
        instead of the unclear "username or\
        password is invalid" message.
        """
        username = self.cleaned_data.get("username")

        if not username:
            return

        if settings.ST_CASE_INSENSITIVE_USERNAMES:
            username = username.lower()

        is_found = (
            User.objects
            .filter(username=username)
            .exists())
        if is_found:
            return

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            username = username.lower()

        is_found_email = (
            User.objects
            .filter(email=username)
            .exists())
        if is_found_email:
            return

        raise forms.ValidationError(
            _("No account matches %(username)s.") % {
                'username': username})

    def clean(self):
        self._validate_username()
        return super(LoginForm, self).clean()


class ResendActivationForm(forms.Form):

    email = forms.CharField(
        label=_("Email"),
        widget=forms.EmailInput,
        max_length=254)

    def clean_email(self):
        email = self.cleaned_data["email"]

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            email = email.lower()

        is_existent = (
            User.objects
            .filter(email=email)
            .exists())
        if not is_existent:
            raise forms.ValidationError(
                _("The provided email does not exists."))

        self.user = (
            User.objects
            .filter(
                email=email,
                st__is_verified=False)
            .order_by('-pk')
            .first())
        if not self.user:
            raise forms.ValidationError(
                _("This account is verified, try logging-in."))

        return email

    def get_user(self):
        return self.user


###################################################

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)


        ########################################################################################
        #email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        #if html_email_template_name is not None:
        #    html_email = loader.render_to_string(html_email_template_name, context)
        #    email_message.attach_alternative(html_email, 'text/html')

        #email_message.send()


        ################################################################
        pomail.send(
            [to_email],
            from_email,
            subject=subject,
            message=body, 
            priority='now',
            context=context
        )

        ################################################################

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = User._default_manager.filter(**{
            '%s__iexact' % User.get_email_field_name(): email,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())


    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = _("There is no user registered with that E-Mail address.")
            self.add_error('email', msg)
        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.clean_email()
                   
        for user in self.get_users(email):                                    
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )
