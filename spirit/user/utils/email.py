# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging

from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.core.mail import send_mail

from post_office import mail

from django.conf import settings as django_settings
from ...core.conf import settings
from .tokens import (
    UserActivationTokenGenerator,
    UserEmailChangeTokenGenerator)

logger = logging.getLogger(__name__)


def sender(request, subject, template_name, context, to):
    site = get_current_site(request)
    context.update({
        'site_name': site.name,
        'domain': site.domain,
        'protocol': 'https' if request.is_secure() else 'http'
    })
    message = render_to_string(template_name, context)


###########################################################
    from_email = 'Seabirds.net <no-reply@seabirds.net>'
###########################################################

    for recipient in to:
        try:
            mail.send(
                recipient,
                from_email,
                subject=subject,
                message=message
                )
        except OSError as err:
            logger.exception(err)


def send_activation_email(request, user):
    subject = _("User activation")
    template_name = 'spirit/user/activation_email.html'
    token = UserActivationTokenGenerator().generate(user)
    context = {'user_id': user.pk, 'token': token}
    sender(request, subject, template_name, context, [user.email, ])


def send_verification_email(request):
    subject = _("New user on seabirds.net")
    template_name = 'spirit/user/new_seabirder.html'
   
    admin_emails = [x[1] for x in django_settings.ADMINS]    
    context = {}
    sender(request,subject,template_name,context,admin_emails)



def send_email_change_email(request, user, new_email):
    subject = _("Email change")
    template_name = 'spirit/user/email_change_email.html'
    token = UserEmailChangeTokenGenerator().generate(user, new_email)
    context = {'token': token, }
    sender(request, subject, template_name, context, [user.email, ])


def send_notification_email(request, topic_notifications, comment):
    # TODO: test, implement
    subject = _("New notification: %(topic_name)s") % {
        'topic_name': comment.topic.title}
    template_name = 'spirit/user/notification_email.html'
    context = {'comment': comment, }
    to = [tn.user.email
          for tn in topic_notifications
          if tn.user.is_subscribed]
    sender(request, subject, template_name, context, to)
