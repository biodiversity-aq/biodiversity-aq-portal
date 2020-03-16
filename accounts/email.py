# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging

from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.core.mail import send_mail

from django.conf import settings as django_settings

from .tokens import (
    UserActivationTokenGenerator,
    UserEmailChangeTokenGenerator)

logger = logging.getLogger(__name__)


def sender(request, subject, template_name, context, to):
    site = get_current_site(request)
    context.update({
        'site_name': "Biodiversity.aq",
        'domain': site.domain,
        'request':request,
        'protocol': 'https' if request.is_secure() else 'http'
    })
    message = render_to_string(template_name, context)


###########################################################
    from_email = django_settings.SENDER_MAIL
###########################################################

    send_mail(
        subject,
        message,
        from_email,
        to,
        fail_silently=False,
    )
    


def send_activation_email(request, user):
    subject = _("User activation")
    template_name = 'registration/activation_email.html'
    token = UserActivationTokenGenerator().generate(user)
    context = {'user_id': user.pk, 'token': token, 'request':request}
    sender(request, subject, template_name, context, [user.email, ])


def send_verification_email(request):
    subject = _("New user on biodiversity.aq")
    template_name = 'registration/new_user.html'
   
    admin_emails = [x[1] for x in django_settings.ADMINS]    
    context = {}

    sender(request,subject,template_name,context, admin_emails)


