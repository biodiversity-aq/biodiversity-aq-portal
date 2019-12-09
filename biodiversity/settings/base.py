"""
Django settings for biodiversity project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, socket
from os import environ

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Add serializationfor geojson
SERIALIZATION_MODULES = {
    "geojson": "django.contrib.gis.serializers.geojson", 
}




GEOS_LIBRARY_PATH = environ.get('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = environ.get('GDAL_LIBRARY_PATH')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'home',
    'search',
    'djgeojson',
    'leaflet',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.styleguide',
    'wagtail.contrib.modeladmin',

    'modelcluster',
    'taggit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.gis',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',


    'gunicorn',
    'captcha',
    'storages',
    'crispy_forms',
    'import_export',
    
    'wagtail.contrib.sitemaps',
    'wagtail.contrib.routable_page',
    'django_social_share',
    'puput',
    'colorful',

    'django_countries',
    'djconfig',
    'data',
    'polaaar'

       
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'djconfig.middleware.DjConfigMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'biodiversity.urls'



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'djconfig.context_processors.config',
            ],
        },
    },
]

WSGI_APPLICATION = 'biodiversity.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

#if socket.gethostname() == "DESKTOP-8K2LJ17" or "HDLT15":
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.contrib.gis.db.backends.postgis',
#            'NAME': 'biodiversity_aq',
#            'USER': 'biodiversity_aq_admin',
#            'PASSWORD': 'bi0diversity',   ##'p0l@radmin!1',
#            'HOST': '',
#            'PORT': '5432'
#        }
#    }
#elif socket.gethostname() == 'DESKTOP-5JDHM1B':
#     DATABASES = {
#        'default': {
#            'ENGINE': 'django.contrib.gis.db.backends.postgis',
#            'NAME': 'biodiversity_aq',
#            'USER': 'biodiversity_aq_admin',
#            'PASSWORD': 'bi0diversity',
#            'HOST': '',
#            'PORT': '5433'
#        }
#    }
#else:        
    

DEBUG=True
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

    import dj_database_url
    
    #db_from_env = dj_database_url.config(conn_max_age=500)
    #DATABASES['default'].update(db_from_env)
    DATABASES['default'] = dj_database_url.config()
    DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

    SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO", 
    "https"
    )


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Wagtail settings

WAGTAIL_SITE_NAME = "biodiversity"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'http://example.com'


SITE_ID = 1


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'


CRISPY_TEMPLATE_PACK = 'bootstrap4'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'testlogger': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}


FORMS_EXTRA_FIELDS = (
    (100, "captcha.fields.ReCaptchaField","ReCaptcha"),
    )



#########################################################################################
#### Django Leaflet settings

LEAFLET_CONFIG = {
    
    'DEFAULT_CENTER':(0,0),    
    'DEFAULT_ZOOM':1,    
    
    }


#############################################
#### Requirement for Puput blog app 
PUPUT_AS_PLUGIN = True


##############################################
#### This is set to eliminate a simple_server.py error related to: https://github.com/wagtail/wagtail/issues/4254
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000



############################################
#### DJANGO ALLAUTH SETTINGS

#ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =1
#ACCOUNT_EMAIL_REQUIRED = True
#ACCOUNT_EMAIL_VERIFICATION = "mandatory"
#ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
#ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400 # 1 day in seconds
#ACCOUNT_LOGOUT_REDIRECT_URL ='/accounts/login/'
#LOGIN_REDIRECT_URL = '/accounts/email/' 


LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'accounts.UserProfile'


ADMINS = (
    #('You', 'wsuadmin@seabirds.net'),
    ('Grant','grwhumphries@blackbawks.net')
)


SENDER_MAIL = 'Seabirds.net <no-reply@seabirds.net>'