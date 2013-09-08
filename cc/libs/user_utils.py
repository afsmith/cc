from django import http
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from cc.apps.accounts.models import CUser as User

import codecs
import csv
import cStringIO as StringIO


class UnknownFormatError(Exception):
    def __init__(self, format):
        self.reason = 'Format %s not supported' % (format,)

    def __str__(self):
        return self.reason


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

        response = http.HttpResponse(
            FileWrapper(result), content_type='text/csv'
        )
        response['Content-Disposition'] = (
            "attachment; filename=\"%s\"" % filename.encode('utf8')
        )
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

    REQUIRED_FIELDS = (
        'first_name',
        'last_name',
        'email',
        'username',
    )

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

        status_msg = {
            'infos': [],
            'errors': [],
            'action': 'add',
        }

        lines_num = len(users_data.readlines())
        if lines_num > settings.MANAGEMENT_CSV_LINES_MAX:
            status_msg['errors'].append(
                _('Imported file has more than maximal number of lines (%d)')
                % (settings.MANAGEMENT_CSV_LINES_MAX,)
            )
            transaction.rollback()
            return status_msg

        users_data.seek(position)
        reader = UnicodeReader(users_data, dialect=dialect)
        header = reader.next()

        # Check for properly filled header
        valid, missing = self._validate_header(header)
        if not valid:
            status_msg['errors'].append(
                _('Missing required header fields: %s.') % ', '.join(missing)
            )
            transaction.rollback()
            return status_msg

        cust_reader = CustomDictReader(
            reader=reader, f=users_data, dialect=dialect, fieldnames=header
        )
        for counter, row in enumerate(cust_reader):
            user = None
            if row['username']:
                try:
                    user = User.objects.get(username=row['username'])
                except User.DoesNotExist:
                    user = None
            else:
                status_msg['errors'].append(
                    _('Missing username field in row %d.') % (counter+1)
                )
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
                        #self._send_add_to_group_internal_message(user)
                        status_msg['infos'].append(
                            _('User %(username)s added to group %(groupname)s.')
                            % {
                                'username': user.username,
                                'groupname': self.group.name,
                            }
                        )
                    else:
                        status_msg['infos'].append(
                            _('User %(username)s (row %(counter)d) already '
                              'assigned to this group, skipping.')
                            % {
                                'username': user.username,
                                'counter': counter+1,
                            }
                        )
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

                userProfile = UserProfile(role=UserProfile.ROLE_RECIPIENT, user=user, phone=phone)
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