# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core import signing
from django.utils.encoding import smart_text
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenGenerator(object):

    def _uid(self, user):
        raise NotImplementedError

    def generate(self, user, data=None):
        
        data = data or {}
        data.update({'uid': self._uid(user), })
        return signing.dumps(data, salt=__name__).replace(":", ".")

    def is_valid(self, user, signed_value):
        try:
            self.data = signing.loads(signed_value.replace(".", ":"), salt=__name__)
        except signing.BadSignature:
            return False

        if self.data['uid'] != self._uid(user):
            return False

        return True


class UserActivationTokenGenerator(TokenGenerator):

    def _uid(self, user):
        return ";".join((smart_text(user.pk), smart_text(user.is_verified)))





class UserEmailChangeTokenGenerator(TokenGenerator):

    def _uid(self, user):
        return ";".join((smart_text(user.pk), smart_text(user.email)))

    def generate(self, user, new_email):
        return super(UserEmailChangeTokenGenerator, self).generate(user, {'new_email': new_email, })

    def get_email(self):
        return self.data['new_email']
