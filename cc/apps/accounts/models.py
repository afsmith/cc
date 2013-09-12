from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, **kwargs):
        if 'email' not in kwargs:
            raise ValueError('Users must have an email address')

        user = self.model(**kwargs)
        user.set_password(kwargs['password'])
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        #user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_receiver_user(self, email):
        '''
        Create the receiver user with just email address
        Generate random password and fill other required fields with N/A
        '''
        random_password = CUser.objects.make_random_password()
        user = self.create_user(
            email=email,
            password=random_password,
            first_name='N/A',
            last_name='N/A',
            country='N/A',
            industry='N/A',
        )
        user.is_active = False
        user.save(using=self._db)
        return user


class CUser(AbstractUser):
    country = models.CharField(_('Country'), max_length=50)
    industry = models.CharField(_('Industry'), max_length=50)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'country',
        'industry',
    ]

# Email should be unique
CUser._meta.get_field('email')._unique = True
CUser._meta.get_field('username')._unique = False
