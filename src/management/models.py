# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Models for application management.
"""

from django import http
from django.conf import settings
from django.contrib.auth.models import Group, User, UserManager
from django.core.servers.basehttp import FileWrapper
from django.core.validators import EmailValidator
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _


import codecs, csv
import cStringIO as StringIO
import cStringIO
from content import utils
#from messages_custom.models import MailTemplate
#from messages_custom.utils import send_email, send_message

class OneClickLinkToken(models.Model):

    user = models.ForeignKey(User)
    token = models.CharField(default=utils.gen_ocl_token, max_length=30, blank=False)
    expired = models.BooleanField(db_index=True, default=False)
    expires_on = models.DateField(_('Expiration date'), null=True, db_index=True)
    allow_login = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s[%s][%s]' % (self.user, self.token, self.expires_on)



class UserGroupProfile(models.Model):
    """Group-specific user profile.

    Currently group-specific profile is created only for users in Admin role.
    It's not needed for normal users, and Superusers have full access to all
    groups anyway.
    """

    LEVEL_HALF_ADMIN = 10
    LEVEL_FULL_ADMIN = 20
    LEVELS = (
        (LEVEL_HALF_ADMIN, 'Half Admin'),
        (LEVEL_FULL_ADMIN, 'Full Admin'),
        )

    user = models.ForeignKey(User, related_name='group_profiles')
    group = models.ForeignKey(Group, related_name='user_profiles')

    access_level = models.IntegerField(_('Access level'),
        choices=LEVELS, default=LEVEL_HALF_ADMIN)

    class Meta:
        unique_together = ('user', 'group')

    def __unicode__(self):
        return '%s (%s in %s)' % (self.user, self.get_access_level_display(), self.group)


class KnetoUserManager(UserManager):
    """ Custom User model manager
    """

    def all(self, *args, **kwargs):
        """ possibility to take in to account
            SALES_PLUS version view
        """
        if settings.SALES_PLUS:
            return super(UserManager, self).all(*args, **kwargs)
        else:
            return super(UserManager, self).all(*args, **kwargs).filter(userprofile__role__lt=40)

    def filter(self, *args, **kwargs):
        """ possibility to take in to account
            SALES_PLUS version view
        """
        if settings.SALES_PLUS:
            return super(UserManager, self).filter(*args, **kwargs)
        else:
            return super(UserManager, self).filter(*args, **kwargs).filter(userprofile__role__lt=40)

class UserProfileManager(models.Manager):
    """ Custom User model manager
    """

    def all(self, *args, **kwargs):
        """ possibility to take in to account
            SALES_PLUS version view
        """
        if settings.SALES_PLUS:
            return super(UserProfileManager, self).all(*args, **kwargs)
        else:
            return super(UserProfileManager, self).all(*args, **kwargs).filter(role__lt=40)

class UserProfile(models.Model):
    """Model specifying additional data for users of the system.
    """

    USERNAME_LENGTH = 299
    FIRST_NAME_LENGTH = 20
    LAST_NAME_LENGTH = 30
    EMAIL_LENGTH = 70
    PHONE_REGEX = '^[\+]?[ ]?([0-9]{1,})+([ ][0-9]{1,})*$'

    ROLE_SUPERADMIN = 10
    ROLE_ADMIN = 20
    ROLE_USER = 30
    ROLE_USER_PLUS = 40

    ROLES = (
        (ROLE_SUPERADMIN, ('admin')),
        (ROLE_ADMIN, _('sender')),
        (ROLE_USER, _('recipient')),
        (ROLE_USER_PLUS, _('OCL recipient')),
    )
    ROLES_CUTED = (
        (ROLE_USER, _('recipient')),
        (ROLE_USER_PLUS, _('OCL recipient')),

    )

    user = models.OneToOneField(User, primary_key=True)
    role = models.IntegerField(_('User role'), choices=ROLES, db_index=True)
    phone = models.CharField(_('Phone number'), max_length=20, blank=True)
    language = models.CharField(_('Language'), choices=settings.LANGUAGES, max_length=7)
    ldap_user = models.BooleanField(_('User from LDAP'), default=False)
    has_card = models.BooleanField(_('Has card'), default=False)

    objects = UserProfileManager()

    #class Meta:
    #    index_together = [['group', 'role']]

    @property
    def is_superadmin(self):
        return self.role == self.ROLE_SUPERADMIN

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_user(self):
        return self.role == self.ROLE_USER
    @property
    def is_user_plus(self):
        return self.role == self.ROLE_USER_PLUS

    def get_user_type(self):
        if self.role in (self.ROLE_ADMIN, self.ROLE_SUPERADMIN):
            return 'sender'
        elif self.role == self.ROLE_USER_PLUS:
            return 'OCL recipient'
        else:
            return 'recipient'

    def get_ldap_marker(self):
        if self.ldap_user:
            return '*'
        else:
            return ''

    def get_sales_plus_marker(self):
        if self.role == self.ROLE_USER_PLUS:
            return '+'
        else:
            return ''

    def __unicode__(self):
        sufix = ''
        if self.role == self.ROLE_USER_PLUS:
            sufix = ' +'
        return "%s %s%s" % (self.user.first_name, self.user.last_name, sufix)


class GroupProfile(models.Model):
    """Extended Group class.
    
    self_register_enabled: show/hide group in self_register module group list.
    """
    group = models.OneToOneField(Group, primary_key=True)
    self_register_enabled = models.BooleanField()

    user_count = models.IntegerField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):

        self.user_count = self.group.user_set.filter(userprofile__role__gt=UserProfile.ROLE_ADMIN).count()
        super(GroupProfile, self).save(*args, **kwargs)


def serialize_user(user):
    user_serial = {
        'id': user.id,
        'name': user.first_name + ' ' + user.last_name + user.get_profile().get_sales_plus_marker(),
        'role': user.get_profile().role
    }

    return user_serial

def serialize_group(group):
    group_serial = {
        'id': group.id,
        'name': group.name,
    }

    return group_serial

def _user_to_dict(user):
    if user is None:
        return {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'username': 'username',
            'password': 'password',
            'phone': 'phone',
            'has_card': 'has_card',
        }

    profile = user.get_profile()
    d = {
        'first_name': user.first_name.encode('utf8'),
        'last_name': user.last_name.encode('utf8'),
        'email': user.email.encode('utf8'),
        'username': user.username.encode('utf8'),
        'password': user.password,
        'phone': profile.phone,
    }
    if settings.STATUS_CHECKBOX:
        d['has_card'] = profile.has_card
        
    return d

class UnknownFormatError(Exception):
    def __init__(self, format):
        self.reason = 'Format %s not supported' % (format,)

    def __str__(self):
        return self.reason

class UserExporter(object):

    """
        Class used for exporting users as CSV.
    """

    FORMAT_CSV = 'csv'

    SUPPORTED_FORMATS = (
        FORMAT_CSV,
    )

    def __init__(self, format='csv', group_name=None):

        if format not in self.SUPPORTED_FORMATS:
            raise UnknownFormatError(format)

        self.format = format
        self.group_name = group_name


    def export_users(self, users):
        result = StringIO.StringIO()
        writer = csv.DictWriter(f=result, fieldnames=_user_to_dict(None).keys())

        #
        # write header for the exported data
        #
        writer.writerow(_user_to_dict(None))

        for user in users:
            writer.writerow(_user_to_dict(user))

        filename = 'export.csv'
        if self.group_name:
            filename = '%s.csv' % self.group_name

        response = http.HttpResponse(FileWrapper(result), content_type='text/csv')
        response['Content-Disposition'] = "attachment; filename=\"%s\"" % filename.encode('utf8')
        response['Content-Length'] = result.tell()
        result.seek(0)
        return response

class UserImporter(object):
    """
        Class used for importing users from csv file to a specified group.
    """

    FORMAT_CSV = 'csv'

    SUPPORTED_FORMATS = (
        FORMAT_CSV,
    )

    REQUIRED_FIELDS = ('first_name',
                       'last_name',
                       'email',
                       'username',)


    def __init__(self, group, importer, format=FORMAT_CSV):
        """
        Constructor.

        :param group: Group to which the users are supposed to be imported.
        :param format: Format of incoming data. Defaults to FORMAT_CSV.
        """

        if format not in self.SUPPORTED_FORMATS:
            raise UnknownFormatError(format)

        self.format = format
        self.group = group
        self.importer = importer


    def _validate_header(self, header):
        """
        Function for validating file header.

        Checks if all the required headers specified in REQUIRED_FIELDS are in place.

        :param header: First row of imported file.
        """
        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            if field not in header:
                missing_fields.append(field)
        if missing_fields:
            return False, missing_fields
        return True, None

    def _check_required_vals(self, row):
        missing_values = []
        for key in row.keys():
            if key in self.REQUIRED_FIELDS and not row[key]:
                missing_values.append(key)
        if missing_values:
            return False, missing_values
        return True, None


    @transaction.commit_manually
    def import_users(self, users_data, admin, is_sendmail=True):

        """
            Function importing users to a group from buffer given as the input data.

            :param users_data: File containing data of users which are supposed to be
                               imported into system. Incoming data is in a CSV format.
                               First row of the file should contain header fields with
                               names specified in REQUIRED_FIELDS tuple.
            :param admin:      Admin or Superadmin who makes import. User will
                               will be used as email sender.

            Return values:
                status_msg - dictionary object containing number of processed rows (field
                             row_num), information messages about imported users (field
                             infos) and error messages which occured during users import
                             (field errors). If any errors occured (errors list is not
                             empty) the whole transaction is rolled back.
        """

        position = users_data.tell()
        dialect = csv.excel
        try:
            dialect = csv.Sniffer().sniff(users_data.read(1024))
        except csv.Error:
            pass
        users_data.seek(position)

        status_msg = {'infos': [],
                      'errors': [],
                      'action': 'add',}

        lines_num = len(users_data.readlines())
        if lines_num > settings.MANAGEMENT_CSV_LINES_MAX:
            status_msg['errors'].append(_('Imported file has more than maximal number of lines (%d)')% (settings.MANAGEMENT_CSV_LINES_MAX,))
            transaction.rollback()
            return status_msg

        users_data.seek(position)
        reader = UnicodeReader(users_data, dialect=dialect)
        header = reader.next()

        #
        # Check for properly filled header
        #
        valid, missing = self._validate_header(header)
        if not valid:
            status_msg['errors'].append(_('Missing required header fields: %s.')% ', '.join(missing))
            transaction.rollback()
            return status_msg

        cust_reader = CustomDictReader(reader=reader,f=users_data,dialect=dialect,fieldnames=header)
        for counter, row in enumerate(cust_reader):
            user = None
            if row['username']:
                try:
                    user = User.objects.get(username=row['username'])
                except User.DoesNotExist:
                    user = None
            else:
                status_msg['errors'].append(_('Missing username field in row %d.')%(counter+1))
                continue

            if user is not None:
                #
                # Checking if only username was provided.
                #
                if row['username'] and not row['first_name'] and not row['last_name'] and not row['email']:
                    if self.group not in user.groups.all():
                        user.groups.add(self.group)
                        self.group.groupprofile.save()
                        user.save()

#AFS                        self._send_add_to_group_internal_message(user)
                        status_msg['infos'].append(_('User %(username)s added to group %(groupname)s.')%{'username':user.username,
                                                                                                        'groupname':self.group.name,})
                    else:
                        status_msg['infos'].append(_('User %(username)s (row %(counter)d) already assigned to this group, skipping.')%{'username':user.username, 'counter':counter+1,})
                #
                # Checking data of user in database if other data except username was provided.
                #
                else:
                    has_vals, missing = self._check_required_vals(row)
                    if not has_vals:
                        status_msg['errors'].append(_('Missing required field values for fields %(mising)s in row %(counter)d')%{'mising':', '.join(missing), 'counter':counter+1,})
                        continue

                    if (user.first_name.lower() != row['first_name'].lower() or
                        user.last_name.lower() != row['last_name'].lower() or
                        user.email != row['email']):
                        status_msg['errors'].append(_('User %s already exists with different personal information.')%(row['username']))

                    else:
                        #
                        # User exists, checking if they are already assigned to this group
                        #
                        if self.group not in user.groups.all():
                            user.groups.add(self.group)
                            self.group.groupprofile.save()
                            user.save()

#AFS                            self._send_add_to_group_internal_message(user)
                            status_msg['infos'].append(_('User %(username)s added to group %(groupname)s.')%{'username':user.username, 'groupname':self.group.name,})
                        else:
                            status_msg['infos'].append(_('User %(username)s (row %(counter)d) already assigned to this group, skipping.')%{'username':user.username, 'counter':counter+1,})
            else:
                #
                # User does not exist, creating new user with supplied data
                #
                has_vals, missing = self._check_required_vals(row)
                if not has_vals:
                    status_msg['errors'].append(_('Missing required field values for fields %(mising)s in row %(counter)d')%{'mising':', '.join(missing), 'counter':counter+1,})
                    continue

                username = row['username'].strip()
                first_name = row['first_name'].strip()
                last_name = row['last_name'].strip()
                email = row['email']
                phone = row['phone'] if 'phone' in row else None

                if 'password' in row and row['password']:
                    password = row['password']
                else:
                    password = User.objects.make_random_password()

                if len(username) > UserProfile.USERNAME_LENGTH:
                    status_msg['errors'].append(_('Username %s is too long.') % username)
                    continue
                elif len(first_name) > UserProfile.FIRST_NAME_LENGTH:
                    status_msg['errors'].append(_('First name %s is too long.') % first_name)
                    continue
                elif len(last_name) > UserProfile.LAST_NAME_LENGTH:
                    status_msg['errors'].append(_('Last name %s is too long.') % last_name)
                    continue
                elif len(email) > UserProfile.EMAIL_LENGTH:
                    status_msg['errors'].append(_('Email %s is too long.') % email)
                    continue
                elif not self.validate_email(email):
                    status_msg['errors'].append(_('Email %s is not valid.') % email)
                    continue
                elif phone and not self.validate_regex(UserProfile.PHONE_REGEX, phone):
                    status_msg['errors'].append(_('Phone %s is not valid.') % phone)
                    continue

                user = User.objects.create_user(username=username, email=email, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.groups.add(self.group)
                self.group.groupprofile.save()
                user.save()

                userProfile = UserProfile(role=UserProfile.ROLE_USER, user=user, phone=phone)
                userProfile.save()

# Not helpful to recive two emails                self._send_add_to_group_internal_message(user)
                if is_sendmail:
                    send_email(recipient=user, user=admin,
                            msg_ident=MailTemplate.MSG_IDENT_WELCOME,
                            msg_data={"[username]":user.username,
                                        "[password]":password})

                status_msg['infos'].append(_('New user %(username)s was created and added to group %(groupname)s')%{'username':user.username, 'groupname':self.group.name})

        status_msg['row_num']=counter+1

        if status_msg['errors']:
            transaction.rollback()
        else:
            transaction.commit()

        return status_msg

    def _send_add_to_group_internal_message(self, recipient):
        params_dict={'[groupname]': self.group.name}
        template = MailTemplate.objects.get(type=MailTemplate.TYPE_INTERNAL, identifier=MailTemplate.MSG_IDENT_WELCOME)
        send_message(sender=self.importer, recipients_ids=[recipient.id],
                     subject=template.populate_params_to_text(template.subject, params_dict),
                     body=template.populate_params(params_dict))

    def validate_email(self, email):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
        
    def validate_regex(self, regex, value):
        from django.core.validators import RegexValidator
        from django.core.exceptions import ValidationError
        try:
            RegexValidator(regex)(value)
            return True
        except ValidationError:
            return False
        
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class CustomDictReader(csv.DictReader):
    """
    A DictReader version which replaces standard inner reader property with the
    reader supplied in the constructor.
    """
    def __init__(self, f, reader, fieldnames=None, restkey=None, restval=None,
                 dialect="excel", *args, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, restkey=restkey, restval=restval,
                 dialect=dialect, *args, **kwds)
        self.reader = reader

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.line_num = self.reader.line_num

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

