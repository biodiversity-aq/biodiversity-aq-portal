"""
WSGI config for biodiversity project.
"""

import os
from dj_static import Cling
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biodiversity.settings.production")
application = Cling(get_wsgi_application())

