
SECRET_KEY = "%(secret_key)s"
NEVERCACHE_KEY = "%(nevercache_key)s"

TEMPLATE_DEBUG = False
DEBUG = False

TIME_ZONE = 'Europe/Helsinki'
STATIC_ROOT = '/opt/kneto/cc/static'

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

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-45345264-2'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'andrew.smith@kneto.com'
EMAIL_HOST_PASSWORD = 'rFUnDlfNA5l)[ncu\'IN6N.P!R'
DEFAULT_FROM_EMAIL = 'cc@kneto.com'
EMAIL_USE_TLS=True

FABRIC = {}