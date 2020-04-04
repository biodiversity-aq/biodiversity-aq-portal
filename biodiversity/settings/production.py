from .base import *
import dj_database_url


DEBUG = False

#try:
#    from .local import *
#except ImportError:
#    pass

BASE_URL = 'https://www.biodiversity.aq'

DATABASES = BIODIVERSITY.DATABASE

    
#db_from_env = dj_database_url.config(conn_max_age=500)
#DATABASES['default'].update(db_from_env)
DATABASES['default'] = dj_database_url.config()
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

SECURE_PROXY_SSL_HEADER = (
"HTTP_X_FORWARDED_PROTO", 
"https")