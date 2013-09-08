from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

INDUSTRY_CHOICES = (
    ('industry-automotive-aerospace', 'Automotive & Aerospace'),
    ('industry-banking-finance', 'Banking & Finance'),
    ('industry-business-consultancy', 'Business Consultancy'),
    ('industry-communications', 'Communications'),
    ('industry-construction', 'Construction'),
    ('industry-document-management', 'Document Management'),
    ('industry-education', 'Education'),
    ('industry-fashion-retail', 'Fashion & Retail'),
    ('industry-government-national-local', 'Government - National & Local'),
    ('industry-human-resources-training', 'Human Resources/Training'),
    ('industry-industrial-engineering', 'Industrial Engineering'),
    ('industry-insurance', 'Insurance'),
    ('industry-it-service-software', 'IT Services/Software'),
    ('industry-legal', 'Legal'),
    ('industry-libraries', 'Libraries'),
    ('industry-manufacturing', 'Manufacturing'),
    ('industry-media-press-publishing', 'Media/Press/Publishing'),
    ('industry-medical-healthcare', 'Medical/Healthcare'),
    ('industry-military-defence', 'Military/Defence'),
    ('industry-transport-logistics', 'Transport/Logistics'),
)


class CustomUserManager(BaseUserManager):
    def create_user(self, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if 'email' not in kwargs:
            raise ValueError('Users must have an email address')

        user = self.model(**kwargs)
        user.set_password(kwargs['password'])
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class CUser(AbstractUser):
    country = models.CharField(
        _('Country'), choices=settings.COUNTRIES, max_length=50
    )
    industry = models.CharField(
        _('Industry'), choices=INDUSTRY_CHOICES, max_length=50
    )

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
