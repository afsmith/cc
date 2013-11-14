
SECRET_KEY = "%(secret_key)s"
NEVERCACHE_KEY = "%(nevercache_key)s"

TEMPLATE_DEBUG = False
DEBUG = False


DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        # DB name or path to database file if using sqlite3.
        "NAME": "%(proj_name)s",
        # Not used with sqlite3.
        "USER": "%(proj_name)s",
        # Not used with sqlite3.
        "PASSWORD": "%(db_pass)s",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "127.0.0.1",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

CACHE_MIDDLEWARE_SECONDS = 60

CACHE_MIDDLEWARE_KEY_PREFIX = "%(proj_name)s"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

ALLOWED_HOSTS = ['127.0.0.1', '.kneto.com']

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-45345264-2'

#Registration:

HUNGER_ALWAYS_ALLOW_VIEWS = (
    'registration_activation_complete',
    'registration_activate',
    'registration_complete',
    'registration_disallowed',
    'accounts_register',
    'home',
    'view_message',
    'track_email',
    'create_event',
    'close_deal',
)



EMAIL_HOST='email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER='AKIAJJKB7ALYUPX5WMCA'
EMAIL_HOST_PASSWORD='Ai3vBfuFTRVA/bhYniE4bT6lGDEvaz+1/1xRF3q7w7hn'
DEFAULT_FROM_EMAIL='cc@kneto.com'
DEFAULT_BCC_EMAIL='app@kneto.fi'
EMAIL_USE_TLS=True
#EMAIL_CONTENT_SUBTYPE='html'

