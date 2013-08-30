import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'webfront.settings'

from django.contrib.auth.models import User, Group
from management.models import KnetoUserManager

# Custom users Manager
User.add_to_class('objects', KnetoUserManager())

# Change ordering for groups and users
User._meta.ordering = ['first_name', 'last_name']
Group._meta.ordering = ['name']

