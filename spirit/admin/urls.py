# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

from . import views

import spirit.user.admin.urls


app_name = 'admin'
urlpatterns = [
    url(r'^$', views.dashboard, name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^config/$', views.config_basic, name='config-basic'),
   
    url(r'^user/', include(spirit.user.admin.urls)),
]
