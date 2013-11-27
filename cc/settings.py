import os
from os import path
import sys
ROOT_PATH = path.join(path.dirname(__file__))

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

# translation and locale
USE_I18N = True
USE_L10N = True
USE_TZ = False

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Name of the directory for the project.
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
#CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIRNAME


# media
MEDIA_ROOT = path.abspath(path.join(ROOT_PATH, 'media'))
MEDIA_URL = '/media/'

# static
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    path.abspath(path.join(ROOT_PATH, 'static')),
)



STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'hunger.middleware.BetaMiddleware',
)

ROOT_URLCONF = 'cc.urls'
WSGI_APPLICATION = 'cc.wsgi.application'

# templates
TEMPLATE_DIRS = (
    path.abspath(path.join(ROOT_PATH, 'templates')),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)


# apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    #--- 3rd party modules ---#
    'south',               # south for DB migration
    'django_extensions',   # django extensions
    'registration',        # django registration (Hieu's fork)
    'djcelery',            # celery for converting files
    'analytical',          # support for many analytic platforms
    'cookielaw',           # EU cookie law banner
    'hunger',              # for managing beta signups and invitations
    'django_nose',         # django nose for testing

    # ----- CC APP  ----- #
    'cc.apps.accounts',
    'cc.apps.cc_messages',
    'cc.apps.content',
    'cc.apps.tracking',
    'cc.apps.cc',          # register cc apps to get the template tags
)

# See http://docs.djangoproject.com/en/dev/topics/logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}



##############################################################################
# Magic comes next
##############################################################################

# import choices for forms
from settings_choices import *

# admin settings
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

HUNGER_ALWAYS_ALLOW_VIEWS = [
    'registration_activation_complete',
    'registration_activate',
    'registration_complete',
    'registration_disallowed',
    'accounts_register',
    'view_message',
    'track_email',
    'create_event',
    'close_deal',
]


TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

##############################################################################
# Account & registration
##############################################################################

AUTH_USER_MODEL = 'accounts.CUser'
ACCOUNT_ACTIVATION_DAYS = 7
DEFAULT_FROM_EMAIL = 'admin@cc.kneto.com'

AUTHENTICATION_BACKENDS = (
    'cc.apps.accounts.auth.CUserModelBackend',
)

##############################################################################
# Files
##############################################################################

CONTENT_UPLOADED_DIR = 'uploads'
CONTENT_AVAILABLE_DIR = 'pub'
CONTENT_INVALID_DIR = 'invalid'
CONTENT_THUMBNAILS_DIR = 'thumbnails'
CONTENT_PREVIEWS_DIR = 'previews'

FILE_UPLOAD_PERMISSIONS = 0644
FILE_UPLOAD_PERMISSIONS_DIRS = 0775

FILE_UPLOAD_MAX_MEMORY_SIZE = 209715200
FILE_UPLOAD_HANDLERS = (
    'cc.libs.handlers.MaxFileMemoryFileUploadHandler',
    'cc.libs.handlers.MaxFileTemporaryFileUploadHandler',
)

PDF_MAX_PAGES = 30




##############################################################################
# Celery
##############################################################################

CELERY_RESULT_BACKEND = 'redis'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_CONNECT_RETRY = True

BROKER_URL = 'redis://localhost:6379/0'

CELERYD_CONCURRENCY = 1
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

'''
CELERYBEAT_SCHEDULE = {
    'delete_expired_files_schedule': {
        'task': 'content.tasks.delete_expired_content',
        'schedule': crontab(minute='0', hour='0', day_of_week='*'),
    },

    'generate_reports_schedule': {
        'task': 'reports.tasks.generate_reports',
        'schedule': crontab(minute='*', hour='*', day_of_week='*'),
    },
    'check_mailbox': {
        'task': 'messages_custom.tasks.check_mailbox',
        'schedule': crontab(minute='*'),
    },
    'check_ocl_expiration': {
        'task': 'management.tasks.check_ocl_expiration',
        'schedule': crontab(minute='*'),
    }
}
'''

###################
# DEPLOY SETTINGS #
###################

# These settings are used by the default fabfile.py provided.
# Check fabfile.py for defaults.

#FABRIC = {
#     "SSH_USER": "", # SSH username
#     "SSH_PASS":  "", # SSH password (consider key-based authentication)
#     "SSH_KEY_PATH":  "", # Local path to SSH key file, for key-based auth
#     "ROLE_DEF": {
#        'staging': ['cc-stage.kneto.com'],
#        'prod': ['cc.kneto.com']
#     },
#     "LIVE_HOSTNAME": { 
#        'staging': ['cc-stage.kneto.com'],
#        'prod': ['cc.kneto.com']
#     },
#     "VIRTUALENV_HOME":  "", # Absolute remote path for virtualenvs
#     "PROJECT_NAME": "", # Unique identifier for project
#     "REQUIREMENTS_PATH": "requirements.txt", # Path to pip requirements, relative to project
#     "GUNICORN_PORT": 8000, # Port gunicorn will listen on
#     "LOCALE": "en_US.UTF-8", # Should end with ".UTF-8"
#     "LIVE_HOSTNAME": "kneto.com", # Host for public site.
#     "REPO_URL": "git@github.com:afsmith/kneto-web.git", # Git or Mercurial remote repo URL for the project
#     "DB_PASS": "", # Live database password
#     "ADMIN_PASS": "", # Live admin user password
#     "SECRET_KEY": SECRET_KEY,
#     "NEVERCACHE_KEY": NEVERCACHE_KEY,
#}

#

##############################################################################
# Testing
##############################################################################

# for testing
if 'test' in sys.argv:
    # remove django hunger middleware in testing
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES.remove('hunger.middleware.BetaMiddleware')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--nologcapture', '--nocapture']


##############################################################################
# Move local settings to bottom so any setting can be overriden
##############################################################################

try:
    from local_settings import *
except ImportError:
    print 'local_settings.py doesnt exist yet. Make sure you have created it.'

################################### THE END ###################################
