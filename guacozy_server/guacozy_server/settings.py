import os

import environ

from django.conf.locale.en import formats as en_formats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('DJANGO_SECRET_KEY', default='abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

# Database

DATABASES = {
    'default': env.db_url('DJANGO_DB_URL', default='sqlite:///db.sqlite3')
}

# Application definition

INSTALLED_APPS = [
    # Django packages
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

# Community packages
INSTALLED_APPS += [
    # MPTT - hierarchical objects structur (for Folders)
    'mptt',
    'django_mptt_admin',

    # Palymorphic - for Connection subclasses (RDP, SSH, VNC)
    'polymorphic',

    # Django-rules permission model, enables discovery of rules.py files
    'rules.apps.AutodiscoverRulesConfig',

    # Django REST Framework
    'rest_framework',

    # Django channels
    'channels',

    # Encrypted model fields
    'encrypted_model_fields',

    # semantic ui forms
    'semanticuiforms',
]

# Application packages
INSTALLED_APPS += [
    'users',
    'backend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'guacozy_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'guacozy_server.wsgi.application'

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
TIME_ZONE = env('DJANGO_TIME_ZONE', default="UTC")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Override time formats
en_formats.DATETIME_FORMAT = "Y-m-d H:i:s"

# Static files
# How static files will be served
STATIC_URL = '/staticfiles/'  # How static files will be served

# Where static files will be placed after collectstatic
STATIC_ROOT = 'staticfiles/'

# Additional static folder
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# This is needed for django-rules to work
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ]
}

# Specify ASGI routing (needed for channels)
ASGI_APPLICATION = "guacozy_server.routing.application"

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Field encryption key
FIELD_ENCRYPTION_KEY = env.str('FIELD_ENCRYPTION_KEY', default='Fg5rOYvc_hUjsWoyOwqW_bm4tuZn9UDbRpN-ajrvvoM=')
