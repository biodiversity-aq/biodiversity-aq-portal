from .base import *
from .secrets import *

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

BASE_URL = 'https://127.0.0.1:8000'

try:
    from .local import *
except ImportError:
    pass

DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'biodiversity_aq',
            'USER': 'biodiversity_aq_admin',
            'PASSWORD': 'bi0diversity',
            'HOST': '',
            'PORT': '5432'
        }
    }


