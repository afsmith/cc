from os.path import join, dirname, abspath
import sys
from celery.schedules import crontab

ROOT_PATH = join(dirname(__file__))

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

# translation and locale
USE_I18N = True
USE_L10N = True
USE_TZ = False

# media
MEDIA_ROOT = abspath(join(ROOT_PATH, 'media'))
MEDIA_URL = '/media/'

# static
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    abspath(join(ROOT_PATH, 'static')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage'
    '.CachedStaticFilesStorage'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'cc.apps.cc_stripe.middleware.ActiveSubscriptionMiddleware',

    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'cc.urls'
WSGI_APPLICATION = 'cc.wsgi.application'

# templates
TEMPLATE_DIRS = (
    abspath(join(ROOT_PATH, 'templates')),
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
    'south',                   # south for DB migration
    'django_extensions',       # django extensions
    'registration',            # django registration (Hieu's fork)
    'djcelery',                # celery for converting files
    'analytical',              # support for many analytic platforms
    'cookielaw',               # EU cookie law banner
    # 'hunger',                 # for managing beta signups and invitations
    'django_nose',             # django nose for testing
    'django_forms_bootstrap',  # needed for django-stripe
    'payments',                # django-stripe
    'pagination',
    'debug_toolbar',

    # ----- CC APP  ----- #
    'cc.apps.accounts',
    'cc.apps.cc_messages',
    'cc.apps.content',
    'cc.apps.tracking',
    'cc.apps.reports',
    'cc.apps.main',        # register main apps to get the template tags
    'cc.apps.cc_stripe',
    'cc.apps.address_book',
)

# disable email for SuspiciousOperation
# http://stackoverflow.com/a/19534738/2527433
from django.core.exceptions import SuspiciousOperation


def skip_suspicious_operations(record):
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
    return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        # Define filter
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
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
    ('Andrew Smith', 'andrew.smith@kneto.fi'),
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
    'home',
    'sendgrid_parse',
]

ALLOWED_HOSTS = ['127.0.0.1', '.kneto.com']

TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

TOS_URL = 'http://kneto.com/terms-of-service/'

MESSAGE_EXPIRED_AFTER = 300  # 10 months ~ 300 days


##############################################################################
# Payments
##############################################################################
from stripe_plans import *

SUBSCRIPTION_REQUIRED_EXCEPTION_URLS = (
    # 'home',
    'auth_login',
    'auth_logout',
    'create_event',
    'payments_subscribe',
    'new_payments_subscribe',
    'payments_ajax_cancel',
    'payments_ajax_subscribe',
    'payments_ajax_change_card',
    'payments_ajax_change_plan',
    'payments_history',
    'payments_webhook',
)

SUBSCRIPTION_REQUIRED_REDIRECT = ('new_payments_subscribe')

STRIPE_PUBLIC_KEY = "pk_test_AAXz4ICYdcu4deHMJGmKJsVB"
STRIPE_SECRET_KEY = "sk_test_804dzBOIcp3RHtJhicEC0Glc"

##############################################################################
# Account & registration
##############################################################################

AUTH_USER_MODEL = 'accounts.CUser'
ACCOUNT_ACTIVATION_DAYS = 7
DEFAULT_FROM_EMAIL = 'cc@kneto.com'

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

SUMMERNOTE_FILE_DIR = 'summernote'

FILE_UPLOAD_PERMISSIONS = 0644
FILE_UPLOAD_PERMISSIONS_DIRS = 0775

FILE_UPLOAD_MAX_MEMORY_SIZE = 41943040  # 40 MB
FILE_UPLOAD_HANDLERS = (
    'cc.libs.handlers.MaxFileMemoryFileUploadHandler',
    'cc.libs.handlers.MaxFileTemporaryFileUploadHandler',
)

PDF_MAX_PAGES = 30
PDF_CONVERT_QUALITY = 150

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

CELERYBEAT_SCHEDULE = {
    'delete_old_content_schedule': {
        'task': 'cc.apps.main.tasks.delete_old_content',
        'schedule': crontab(minute=0, hour=0),  # once per day at midnight
    },
}

##############################################################################
# Testing
##############################################################################

# for testing
if 'test' in sys.argv:
    STATICFILES_STORAGE = (
        'django.contrib.staticfiles.storage'
        '.StaticFilesStorage'
    )
    SUBSCRIPTION_REQUIRED_EXCEPTION_URLS += (
        'upload_file',
        'accounts_register'
    )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--nologcapture', '--nocapture', '--verbosity=2']

FIXTURE_DIRS = (
    abspath(join(ROOT_PATH, 'fixtures')),
)


###################
# DEPLOY SETTINGS #
###################

FABRIC_GLOBAL = {
    'REPO_URL': 'git@github.com:afsmith/cc.git',
    'ROLE_DEF': {
        'staging': ['cc-stage.kneto.com'],
        'prod': ['cc.kneto.com']
    },
    'LIVE_HOSTNAME': {
        'staging': 'cc-stage.kneto.com',
        'prod': 'cc.kneto.com',
    },
    'LIVE_CERT': {
        'staging': 'cc.crt',
        'prod': 'cc_kneto_com.pem',
    },
    'LIVE_KEY': {
        'staging': 'cc.key',
        'prod': 'cc01.key',
    },

    'PROJECT_NAME': 'cc',
    'LOCALE': 'en_US.UTF-8',  # Should end with ".UTF-8"
    'REQUIREMENTS_PATH': 'requirements.txt',
    'GUNICORN_PORT': 8000,
    'VIRTUALENV_HOME':  '/opt/kneto',
}

FLEXPAPER_KEY = '$ccd1b1d26f39cf5ec44'
PAY_KEY = 'A923C5'

##############################################################################
# Move local settings to bottom so any setting can be overriden
##############################################################################

try:
    from local_settings import *
except ImportError:
    print 'local_settings.py doesnt exist yet. Make sure you have created it.'

# merge FABRIC settings
FABRIC.update(FABRIC_GLOBAL)

################################### THE END ###################################
