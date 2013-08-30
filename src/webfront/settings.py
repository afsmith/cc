import os.path
from celery.schedules import crontab
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, PosixGroupType
#################
import logging

#TODO handle logging properly via config file!!

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

logger = logging.getLogger('nginx_config')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

logger = logging.getLogger('assignments')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

logger = logging.getLogger('messages_custom')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

logger = logging.getLogger('management')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

##################

NAME = ''
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s
LANGUAGES = (
    ('en', gettext_noop('English')),
    ('fi', gettext_noop('Finnish')),
    ('sv', gettext_noop('Swedish')),
    ('ar', gettext_noop('Arabic')),
    ('bg', gettext_noop('Bulgarian')),
    ('bn', gettext_noop('Bengali')),
    ('bs', gettext_noop('Bosnian')),
    ('ca', gettext_noop('Catalan')),
    ('cs', gettext_noop('Czech')),
    ('cy', gettext_noop('Welsh')),
    ('da', gettext_noop('Danish')),
    ('de', gettext_noop('German')),
    ('el', gettext_noop('Greek')),
    ('en-gb', gettext_noop('British English')),
    ('es', gettext_noop('Spanish')),
    ('es-ar', gettext_noop('Argentinian Spanish')),
    ('et', gettext_noop('Estonian')),
    ('eu', gettext_noop('Basque')),
    ('fa', gettext_noop('Persian')),
    ('fr', gettext_noop('French')),
    ('fy-nl', gettext_noop('Frisian')),
    ('ga', gettext_noop('Irish')),
    ('gl', gettext_noop('Galician')),
    ('he', gettext_noop('Hebrew')),
    ('hi', gettext_noop('Hindi')),
    ('hr', gettext_noop('Croatian')),
    ('hu', gettext_noop('Hungarian')),
    ('id', gettext_noop('Indonesian')),
    ('is', gettext_noop('Icelandic')),
    ('it', gettext_noop('Italian')),
    ('ja', gettext_noop('Japanese')),
    ('ka', gettext_noop('Georgian')),
    ('km', gettext_noop('Khmer')),
    ('kn', gettext_noop('Kannada')),
    ('ko', gettext_noop('Korean')),
    ('lt', gettext_noop('Lithuanian')),
    ('lv', gettext_noop('Latvian')),
    ('mk', gettext_noop('Macedonian')),
    ('ml', gettext_noop('Malayalam')),
    ('mn', gettext_noop('Mongolian')),
    ('nl', gettext_noop('Dutch')),
    ('no', gettext_noop('Norwegian')),
    ('nb', gettext_noop('Norwegian Bokmal')),
    ('nn', gettext_noop('Norwegian Nynorsk')),
    ('pl', gettext_noop('Polish')),
    ('pt', gettext_noop('Portuguese')),
    ('pt-br', gettext_noop('Brazilian Portuguese')),
    ('ro', gettext_noop('Romanian')),
    ('ru', gettext_noop('Russian')),
    ('sk', gettext_noop('Slovak')),
    ('sl', gettext_noop('Slovenian')),
    ('sq', gettext_noop('Albanian')),
    ('sr', gettext_noop('Serbian')),
    ('sr-latn', gettext_noop('Serbian Latin')),
    ('ta', gettext_noop('Tamil')),
    ('te', gettext_noop('Telugu')),
    ('th', gettext_noop('Thai')),
    ('tr', gettext_noop('Turkish')),
    ('uk', gettext_noop('Ukrainian')),
    ('vi', gettext_noop('Vietnamese')),
    ('zh-cn', gettext_noop('Simplified Chinese')),
    ('zh-tw', gettext_noop('Traditional Chinese')),
)

AVAILABLE_LANGUAGES = (
    ('en', gettext_noop('English')),
    ('fi', gettext_noop('Finnish')),
    ('sv', gettext_noop('Swedish')),
)
SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(ROOT_DIR, 'media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

FILE_UPLOAD_PERMISSIONS = 0644
FILE_UPLOAD_PERMISSIONS_DIRS = 0775

FILE_UPLOAD_MAX_MEMORY_SIZE = 209715200 

FILE_UPLOAD_HANDLERS = (
#    "administration.models.MaxFileMemoryFileUploadHandler",
#    "administration.models.MaxFileTemporaryFileUploadHandler",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # The HTTP 403 exception
    'plato_common.middleware.Http403Middleware',
)

ROOT_URLCONF = 'webfront.urls'

SESSION_COOKIE_AGE = 10800

TEMPLATE_DIRS = (
    os.path.join(ROOT_DIR, 'templates'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    #'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    #'messages.context_processors.inbox',
)
INSTALLED_APPS = (
    # Built-in applications.
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Third-party applications.
    'django_extensions',
    'djcelery',
    'gunicorn',
    'south',
    #'messages',
    'djcelery_email',

    # Our applications.
    #'administration',
    'content',
    'management',
    #'assignments',
    'tracking',
    #'tagging',
    #'messages_custom',
    #'notepad',
    #'reports',
    #'self_register',
    #'longerusername',
)

REGISTRATION_OPEN = True
SALES_PLUS = True
ENABLE_MODULES_SIGNOFF = True

TEST_RUNNER = 'bls_common.bls_django.CeleryTestRunner'

import djcelery
djcelery.setup_loader()


#
# Number of files per page returned from content search.
#
CONTENT_PAGE_SIZE = 8

CONTENT_UPLOADED_DIR = 'uploads'
CONTENT_INVALID_DIR = 'invalid'
CONTENT_AVAILABLE_DIR = 'pub'
CONTENT_THUMBNAILS_DIR = 'thumbnails'
CONTENT_PREVIEWS_DIR = 'previews'


#
# Maximum file upload size in Nginx
#

NGINX_CONFIG_FILE_DIR = '/etc/nginx'
NGINX_CONF_FILE = 'nginx.conf'
NGINX_CONFIG_MAKE_BACKUPS=False

#
# OpenOffice Converters properties
#
OO_CONVERTER_PORT = 8100

# RFID card status checkbox feature
STATUS_CHECKBOX = False

#
# Report files paths
#
REPORTS_ROOT = os.path.join(MEDIA_ROOT, 'reports')
REPORTS_TEMPLATES_URL = os.path.join(MEDIA_URL, 'reports/templates')
REPORTS_RESULTS_URL = os.path.join(MEDIA_URL, 'reports/results')
REPORTS_TEMPLATES_DIR = os.path.join(REPORTS_ROOT, 'templates')
REPORTS_RESULTS_DIR = os.path.join(REPORTS_ROOT, 'results')
REPORTS_ENGINE_DIR = os.path.normpath(os.path.join(ROOT_DIR, '../reports/engine/target/plato-reports.jar'))

##############################################################################
# Configuration of the Scorm Importer and Scorm Player.
##############################################################################

#
# Base directory from which the importer should be run.
#
# Importer assumes that its dependencies are located in a ``lib`` subdirectory
# in this path.
#
SCORM_IMPORTER_BASE_DIR = '/opt/bls/scorm'

#
# Full path to the importer's JAR.
#
SCORM_IMPORTER = os.path.join(SCORM_IMPORTER_BASE_DIR, 'reload-import.jar')

#
# Full path to the importer's and player's configuration file.
#
SCORM_IMPORTER_CONF = os.path.join(
    SCORM_IMPORTER_BASE_DIR,
    'conf/reload-system.xml')

#
# Base URL to Scorm Player which should be used to start a course.
#
SCORM_PLAYER_ENDPOINT = '/reload/ScormLaunch'
SCORM_PLAYER_READER_URL = 'http://192.168.0.109:8080/reload/ScormReader'

#
# URL with the login form, here users log into the system.
#

LOGIN_URL = '/accounts/login/'


#
# URL to which user is redirected after successful login.
#
LOGIN_REDIRECT_URL = '/'


AUTH_PROFILE_MODULE = 'management.UserProfile'

#
# Maximal number of rows in imported CSV file
#
MANAGEMENT_CSV_LINES_MAX = 500


##############################################################################
# Tags autocomplete
##############################################################################

SPELL_CHECKER_ENABLED = True
SPELL_CHECKER_MIN_TERM_LENGTH = 4
SPELL_CHECKER_MIN_RATIO = 0.8

##############################################################################
# Celery Configuration
##############################################################################

CELERY_RESULT_BACKEND = 'redis'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_CONNECT_RETRY = True

BROKER_BACKEND = 'redis'
BROKER_HOST = REDIS_HOST
BROKER_PORT = REDIS_PORT
BROKER_VHOST = "0"

CELERYD_CONCURRENCY = 1
#CELERYD_LOG_FILE = 'celeryd.log'
#CELERYD_LOG_LEVEL = 'DEBUG'

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
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

##############################################################################
# Email
##############################################################################

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
CELERY_EMAIL_TASK_CONFIG = {'default_retry_delay': 60, 'max_retries': 3}

EMAIL_HOST='localhost'
EMAIL_PORT=1025

#EMAIL_HOST='email-smtp.us-east-1.amazonaws.com'
#EMAIL_HOST_USER='AKIAJJKB7ALYUPX5WMCA'
#EMAIL_HOST_PASSWORD='Ai3vBfuFTRVA/bhYniE4bT6lGDEvaz+1/1xRF3q7w7hn'
#DEFAULT_FROM_EMAIL='sales@kneto.fi'
#EMAIL_USE_TLS=True
EMAIL_CONTENT_SUBTYPE='html'

###################################################
# setting required by messages_custom.tasks.check_mailbox() task
#EMAIL_BOX_TYPE = 'pop3'
#EMAIL_BOX_HOST = 'pop3.kneto.fi'
#EMAIL_BOX_PORT = 995
#EMAIL_BOX_USER = 'sales@kneto.fi'
#EMAIL_BOX_PASSWORD = 'password'
#EMAIL_BOX_SSL = True
#EMAIL_BOX_REMOVE_MESSAGES = True
#EMAIL_BOX_IMAP_FOLDER = 'INBOX'


#CKEDITOR_UPLOAD_WWW_PATH = 'http://your_domain/media/uploaded-images/'

try:
    from local_settings import *
except ImportError:
    print 'Cannot import webfront.local_settings. Exiting.'
    raise SystemExit(3)

##############################################################################
# Default GUI elements values
##############################################################################
DEFAULT_GUI_WEB_TITLE = 'CUSTOM WEB TITLE'
DEFAULT_GUI_FOOTER = 'Company name | All rights reserved'
CSS_TEMPLATES_DIR = os.path.join(MEDIA_ROOT, 'custom')
CSS_TEMPLATES_URL = os.path.join(MEDIA_URL, 'custom')
CUSTOM_LOGO_FILE_NAME = 'custom_logo'
CUSTOM_BG_FILE_NAME = 'custom_bg.png'
CUSTOM_CSS_FILE_NAME = 'custom.less'
CUSTOM_APPLICATION_ICONS_NAME = 'custom_icons.png'
CUSTOM_FILETYPE_ICONS_NAME = 'custom_file_type.png'
CUSTOM_PROGRESS_ICONS_NAME = 'custom_progress.png'
CUSTOM_MAIN_MENU_BAR_NAME = 'custom_wide.png'

DEFAULT_LOGO_FILE_NAME = 'default_logo'
DEFAULT_BG_FILE_NAME = 'kneto-bg.png'
DEFAULT_CSS_FILE_NAME = 'default.less'
DEFAULT_APPLICATION_ICONS_NAME = 'sprite_icons.png'
DEFAULT_FILETYPE_ICONS_NAME = 'sprite_file_type.png'
DEFAULT_PROGRESS_ICONS_NAME = 'sprite_progress.png'
DEFAULT_MAIN_MENU_BAR_NAME = 'sprite_wide.png'

#GOODBYE_EMAIL_SUBJECT = "Goodbye!"
#GOODBYE_EMAIL_MESSAGE = "Bye!"

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploaded-images')
CKEDITOR_UPLOAD_URL = '/media/uploaded-images/'

##############################################################################
# LDAP
##############################################################################

AUTH_LDAP_MIRROR_GROUPS = True

AUTHENTICATION_BACKENDS = (
#    'ldap_backend.backend.PlatoLDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
