from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import re_path, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from puput import urls as puput_urls

from search import views as search_views

from django.contrib.auth import views as auth_views

import accounts
import data.urls
import polaaar.urls

urlpatterns = [
    re_path(r'^django-admin/', admin.site.urls),


    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^accounts/', include('accounts.urls')), 
    url(r'^accounts/', include('django.contrib.auth.urls'), name='accounts'),

    path('data/', include('data.urls')),
    re_path(r'polaaar/', include('polaaar.urls')),
    path('www/', include('home.urls')),
    # re_path(r'users/',include('users.urls')),

    url(r'^data/',include('data.urls')),
    url(r'^polaaar/',include('polaaar.urls')),
    

    url(r'',include(puput_urls)),
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    re_path(r'', include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    url(r'^pages/', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
