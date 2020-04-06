from .base import *
import dj_database_url
from .secrets import * 

DEBUG = False

#try:
#    from .local import *
#except ImportError:
#    pass

#BASE_URL = 'https://www.biodiversity.aq'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'd86hngmf7e303f',
        'USER': 'hwyoarfegnhrwn',
        'PASSWORD': '286e142ad8f2d8aa4d5ad529c43bbe847f4037ddc4f065f51bf18366cfac4cd5',
        'HOST': 'ec2-54-217-234-157.eu-west-1.compute.amazonaws.com',
        'PORT': '5432'
    }
}
#BIODIVERSITYDATABASE

    
#db_from_env = dj_database_url.config(conn_max_age=500)
#DATABASES['default'].update(db_from_env)
DATABASES['default'] = dj_database_url.config()
#DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

SECURE_PROXY_SSL_HEADER = (
"HTTP_X_FORWARDED_PROTO", 
"https")