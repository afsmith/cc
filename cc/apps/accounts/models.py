from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cc.libs.utils import gen_ocl_token


class CustomUserManager(BaseUserManager):
    '''
    Custom User manager
    '''
    def create_user(self, **kwargs):
        if 'email' not in kwargs:
            raise ValueError('Users must have an email address')
        # turn user email to lowercase on saving
        kwargs['email'] = kwargs['email'].lower()

        try:
            user = CUser.objects.get(email__iexact=kwargs['email'])
            user = CUser(id=user.id, **kwargs)
        except CUser.DoesNotExist:
            user = self.model(**kwargs)
        user.set_password(kwargs['password'])
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
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
    '''
    Custom User model
    '''
    country = models.CharField(_('Country'), max_length=50)
    industry = models.CharField(_('Industry'), max_length=50)
    signature = models.TextField(_('Signature'), blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'country',
        'industry',
    ]

    def get_invitations(self):
        try:
            if not self.customer.has_active_subscription:
                return False
        except:
            return False
        else:
            current_plan = self.customer.current_subscription.plan
            invitations = settings.PAYMENTS_PLANS[
                current_plan
            ]['metadata']['users'] - 1
            return invitations


# Email should be unique
CUser._meta.get_field('email')._unique = True
CUser._meta.get_field('username')._unique = False


class OneClickLinkToken(models.Model):
    '''
    One click link (OCL) token model
    '''
    user = models.ForeignKey(CUser)
    token = models.CharField(default=gen_ocl_token, max_length=30, blank=False)
    expired = models.BooleanField(db_index=True, default=False)
    expires_on = models.DateField(
        _('Expiration date'), null=True, db_index=True
    )
    allow_login = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s[%s][%s]' % (self.user, self.token, self.expires_on)


class BillingAddress(models.Model):
    '''
    Users billing address provided by stripe webhook
    '''
    user = models.ForeignKey(CUser)
    name = models.CharField(_('Name'), max_length=128, null=True)
    address_line1 = models.CharField(
        _('Address line1'), max_length=128, null=True
    )
    address_line2 = models.CharField(
        _('Address line2'), max_length=128, null=True
    )
    address_zip = models.CharField(_('Zip'), max_length=20, null=True)
    address_city = models.CharField(_('City'), max_length=50, null=True)
    address_state = models.CharField(_('State'), max_length=50, null=True)
    address_country = models.CharField(_('Country'), max_length=50, null=True)

    def __unicode__(self):
        return '{} - {}'.format(self.name, self.address_line1)


class Invitation(models.Model):
    '''
    Invitation model for user who purchased multiple seats to invite
    other users
    '''

    STATUS_SENT = 'SENT'
    STATUS_ACCEPTED = 'ACCEPTED'

    from_user = models.ForeignKey(CUser, related_name='invites_sent')
    to_user = models.ForeignKey(
        CUser, null=True, related_name='invites_receive', unique=True
    )
    to_email = models.CharField(_('Email'), max_length=75, unique=True)
    code = models.CharField(max_length=30, default=gen_ocl_token)
    status = models.CharField(max_length=30, default=STATUS_SENT)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{} - {}'.format(self.to_email, self.status)
