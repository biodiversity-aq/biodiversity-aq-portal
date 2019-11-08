# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import hashlib

from django.utils.http import urlencode, urlquote

from .registry import register

from django.contrib.auth import get_user_model
User = get_user_model()

@register.simple_tag()
def get_gravatar_url(user, size, rating='g', default='identicon'):
    url = "https://www.gravatar.com/avatar/"
    hash = hashlib.md5(user.email.strip().lower().encode('utf-8')).hexdigest()
    data = urlencode([('d', urlquote(default)),
                      ('s', str(size)),
                      ('r', rating)])
    return "".join((url, hash, '?', data))


######## Custom code for listing all users as the one above means you need to draw all data and this is cumbersome... #########

@register.simple_tag()
def get_gravatar(userpk, size, rating='g', default='identicon'):
    url = "https://www.gravatar.com/avatar/"

    email = User.objects.filter(pk=userpk).values_list('email')[0][0]
    

    hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    data = urlencode([('d', urlquote(default)),
                      ('s', str(size)),
                      ('r', rating)])
    return "".join((url, hash, '?', data))
