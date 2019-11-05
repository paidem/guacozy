import logging
import os

import environ
from django.conf.locale.en import formats as en_formats
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('DJANGO_SECRET_KEY', default='abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Name in grapelli-admin
GRAPPELLI_ADMIN_TITLE = "Guacozy Administration"

# Database

DATABASES = {
    'default': env.db_url('DJANGO_DB_URL', default='sqlite:///db.sqlite3')
}

# Application definition

INSTALLED_APPS = [
    # Grapelli admin
    'grappelli',

    # Django packages
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
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

    # list filters
    'django_admin_listfilter_dropdown',
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


# Try using CACHE_URL env and fallback to user local memory cache if not configured


CACHES = {
    'default': env.cache('CACHE_URL', default='locmemcache://'),
}

# Production uses memcached for CACHE_URL (so all instances of Daphne server can access session info)
# Using cache as session engine and locmemcache as cache will result session clearing
# after each restart of application (you will have to login again)
# So in DEV environment you can either spin up your own memcached instance and specify it, e.g.
# CACHE_URL=memcache://192.168.99.100:11211
# or you can use file backend as session engine.
if DEBUG and CACHES['default']['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache':
    SESSION_ENGINE = "django.contrib.sessions.backends.file"

    # Override default SESSION_FILE_PATH (which default to tempfile.gettempdir())
    # because it WILL contain your passwords and you DON'T want them hanging there, where other people might see
    # so we use 'tmp' folder in Django root folder and add it to .gitignore
    SESSION_FILE_PATH = os.path.join(BASE_DIR, 'tmp')
    if not os.path.exists(SESSION_FILE_PATH):
        os.mkdir(SESSION_FILE_PATH)
else:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"

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
AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

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

#
# LDAP authentication (optional)
#

try:
    from guacozy_server import ldap_config as LDAP_CONFIG
except ImportError:
    LDAP_CONFIG = None

if LDAP_CONFIG is not None:
    # Check that django_auth_ldap is installed
    try:
        import ldap
        import django_auth_ldap
    except ImportError:
        raise ImproperlyConfigured(
            "LDAP authentication has been configured, but django-auth-ldap is not installed. Remove "
            "guacozy_server/ldap_config.py to disable LDAP."
        )

    # Required configuration parameters
    try:
        AUTH_LDAP_SERVER_URI = getattr(LDAP_CONFIG, 'AUTH_LDAP_SERVER_URI')
    except AttributeError:
        raise ImproperlyConfigured(
            "Required parameter AUTH_LDAP_SERVER_URI is missing from ldap_config.py."
        )

    # Optional configuration parameters
    AUTH_LDAP_ALWAYS_UPDATE_USER = getattr(LDAP_CONFIG, 'AUTH_LDAP_ALWAYS_UPDATE_USER', True)
    AUTH_LDAP_AUTHORIZE_ALL_USERS = getattr(LDAP_CONFIG, 'AUTH_LDAP_AUTHORIZE_ALL_USERS', False)
    AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = getattr(LDAP_CONFIG, 'AUTH_LDAP_BIND_AS_AUTHENTICATING_USER', False)
    AUTH_LDAP_BIND_DN = getattr(LDAP_CONFIG, 'AUTH_LDAP_BIND_DN', '')
    AUTH_LDAP_BIND_PASSWORD = getattr(LDAP_CONFIG, 'AUTH_LDAP_BIND_PASSWORD', '')
    AUTH_LDAP_CACHE_TIMEOUT = getattr(LDAP_CONFIG, 'AUTH_LDAP_CACHE_TIMEOUT', 0)
    AUTH_LDAP_CONNECTION_OPTIONS = getattr(LDAP_CONFIG, 'AUTH_LDAP_CONNECTION_OPTIONS', {})
    AUTH_LDAP_DENY_GROUP = getattr(LDAP_CONFIG, 'AUTH_LDAP_DENY_GROUP', None)
    AUTH_LDAP_FIND_GROUP_PERMS = getattr(LDAP_CONFIG, 'AUTH_LDAP_FIND_GROUP_PERMS', False)
    AUTH_LDAP_GLOBAL_OPTIONS = getattr(LDAP_CONFIG, 'AUTH_LDAP_GLOBAL_OPTIONS', {})
    AUTH_LDAP_GROUP_SEARCH = getattr(LDAP_CONFIG, 'AUTH_LDAP_GROUP_SEARCH', None)
    AUTH_LDAP_GROUP_TYPE = getattr(LDAP_CONFIG, 'AUTH_LDAP_GROUP_TYPE', None)
    AUTH_LDAP_MIRROR_GROUPS = getattr(LDAP_CONFIG, 'AUTH_LDAP_MIRROR_GROUPS', None)
    AUTH_LDAP_MIRROR_GROUPS_EXCEPT = getattr(LDAP_CONFIG, 'AUTH_LDAP_MIRROR_GROUPS_EXCEPT', None)
    AUTH_LDAP_PERMIT_EMPTY_PASSWORD = getattr(LDAP_CONFIG, 'AUTH_LDAP_PERMIT_EMPTY_PASSWORD', False)
    AUTH_LDAP_REQUIRE_GROUP = getattr(LDAP_CONFIG, 'AUTH_LDAP_REQUIRE_GROUP', None)
    AUTH_LDAP_NO_NEW_USERS = getattr(LDAP_CONFIG, 'AUTH_LDAP_NO_NEW_USERS', False)
    AUTH_LDAP_START_TLS = getattr(LDAP_CONFIG, 'AUTH_LDAP_START_TLS', False)
    AUTH_LDAP_USER_QUERY_FIELD = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_QUERY_FIELD', None)
    AUTH_LDAP_USER_ATTRLIST = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_ATTRLIST', None)
    AUTH_LDAP_USER_ATTR_MAP = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_ATTR_MAP', {})
    AUTH_LDAP_USER_DN_TEMPLATE = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_DN_TEMPLATE', None)
    AUTH_LDAP_USER_FLAGS_BY_GROUP = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_FLAGS_BY_GROUP', {})
    AUTH_LDAP_USER_SEARCH = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_SEARCH', None)
    AUTH_LDAP_DEBUG = getattr(LDAP_CONFIG, 'AUTH_LDAP_DEBUG', False)

    # Optionally disable strict certificate checking
    if getattr(LDAP_CONFIG, 'LDAP_IGNORE_CERT_ERRORS', False):
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    # Prepend LDAPBackend to the authentication backends list
    # LDAPBackend does not inherit from ModelBackend.
    # It is possible to use LDAPBackend exclusively by configuring it to
    # draw group membership from the LDAP server.
    # However, if you would like to assign permissions to individual users or add
    # users to groups within Django, you’ll need to have both backends installed:
    AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')

    # Enable logging for django_auth_ldap
    ldap_logger = logging.getLogger('django_auth_ldap')
    ldap_logger.addHandler(logging.StreamHandler())
    ldap_logger.setLevel(logging.INFO)

    # Enable DEBUG level if AUTH_LDAP_DEBUG or DEBUG is True
    if AUTH_LDAP_DEBUG or DEBUG:
        ldap_logger.setLevel(logging.DEBUG)
