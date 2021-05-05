from .base import *

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

BASE_URL = 'https://127.0.0.1:8000'

GEOSERVER_HOST = 'http://sandbox.bebif.be/geoserver/antabif/wms?'

GEOSERVER_NAMESPACE = 'antabif'

try:
    from .local import *
except ImportError:
    pass



