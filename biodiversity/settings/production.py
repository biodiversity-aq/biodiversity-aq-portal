from .base import *
import dj_database_url
from .secrets import * 

DEBUG = False

try:
    from .local import *
except ImportError:
    pass

#BASE_URL = 'https://www.biodiversity.aq'

DATABASES = BIOD_DATABASE


DATABASES['default'] = dj_database_url.config()
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

SECURE_PROXY_SSL_HEADER = (
"HTTP_X_FORWARDED_PROTO", 
"https"
    
