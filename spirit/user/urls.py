# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from .auth import urls as auth_urls
from . import views


app_name = 'user'
urlpatterns = [
    url(r'^$', views.update, name='update'),
    url(r'^confirm-delete/$',views.confirm_delete,name='confirm-delete'),
    url(r'^delete-account/$',views.delete_profile,name='delete-profile'),
    url(r'^password-change/$', views.password_change, name='password-change'),
    url(r'^email-change/$', views.email_change, name='email-change'),
    url(r'^email-change/(?P<token>[0-9A-Za-z_\-\.]+)/$',
        views.email_change_confirm,
        name='email-change-confirm'),

    
    url(r'^menu/$', views.menu, name='menu'),

    url(r'^', include(auth_urls)),
]
