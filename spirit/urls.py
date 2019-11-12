# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

import spirit.admin.urls
import spirit.user.urls


app_name = 'spirit'
urlpatterns = [    
    url(r'^st/admin/', include(spirit.admin.urls)),
    url(r'^user/', include(spirit.user.urls)),
]
