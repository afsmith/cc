from .baseconv import BaseConv

from mdetect import UAgentInfo
from os.path import join, dirname, abspath
import datetime
import random
import pygeoip


def get_domain(request):
    '''
    Get the domain name from request
    '''
    protocol = 'http'
    if request.is_secure():
        protocol = 'https'

    return '%s://%s' % (protocol, request.get_host())


def get_client_ip(request):
    '''
    Get the client IP from request
    '''
    address_list = request.META.get('HTTP_X_FORWARDED_FOR')
    if address_list:
        client_ip = address_list.split(',')[-1].strip()
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    return client_ip


def get_device_name(request):
    '''
    Get the device name from request
    '''
    user_agent = request.META.get('HTTP_USER_AGENT')
    http_accept = request.META.get('HTTP_ACCEPT')
    if user_agent and http_accept:
        agent = UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
        if agent.detectMobileQuick():
            if agent.detectIphone():
                return 'iPhone'
            elif agent.detectIpod():
                return 'iPod'
            elif agent.detectAndroidPhone():
                return 'Android phone'
            elif agent.detectWindowsPhone():
                return 'Windows Phone'
            elif agent.detectBlackBerry():
                return 'BlackBerry'
            elif agent.detectSymbianOS():
                return 'Symbian'
            else:
                return 'Mobile phone'
        elif agent.detectTierTablet():
            if agent.detectIpad():
                return 'iPad'
            elif agent.detectAndroidTablet():
                return 'Android tablet'
            elif agent.detectBlackBerryTablet():
                return 'BlackBerry tablet'
            elif agent.detectWebOSTablet():
                return 'WebOS tablet'
        else:
            return 'Desktop'
    else:
        raise ValueError('Invalid request')


def get_location(request):
    client_ip = get_client_ip(request)
    gi = pygeoip.GeoIP(abspath(join(dirname(__file__), 'GeoLiteCity.dat')))
    location = ''
    try:
        location_dict = gi.record_by_addr(client_ip)
    except pygeoip.GeoIPError:
        return location
    if location_dict:
        location = '{}, {}'.format(
            location_dict['city'], location_dict['country_code']
        )
    return location


def progress_formatter(progress):
    '''
    Return the nicely rounded progress
    '''
    if progress == 0:
        return 0
    elif progress < 0.15:
        return 10
    elif progress > 0.85 and progress < 1:
        return 90

    return int(round(progress * 10) * 10)


def dictfetchall(cursor):
    '''
    Returns all rows from a cursor as a dict
    '''
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def sql(queryset):
    '''
    Returns the raw SQL of the queryset
    '''
    return queryset.query.__str__()


def format_dbtime(time_from_db):
    '''
    Format time from second to HH:MM:SS format
    '''
    if time_from_db is None:
        return '00:00:00'
    time_in_second = time_from_db / 10.0
    #return str(datetime.timedelta(seconds=time_in_second))
    m, s = divmod(time_in_second, 60)
    h, m = divmod(m, 60)
    return '{0:02.0f}:{1:02.0f}:{2:04.1f}'.format(h, m, s)


def get_hours_until_now(datetime_obj):
    # get now object
    now_obj = datetime.datetime.now()
    # get timedelta difference
    diff = now_obj - datetime_obj
    # calculate the diff in h, m, s
    m, s = divmod(diff.days * 86400 + diff.seconds, 60)
    h, m = divmod(m, 60)
    return h


class DotExpandedDict(dict):
    """
    A special dictionary constructor that takes a dictionary in which the keys
    may contain dots to specify inner dictionaries. It's confusing, but this
    example should make sense.

    >>> d = DotExpandedDict({'person.1.firstname': ['Simon'], \
            'person.1.lastname': ['Willison'], \
            'person.2.firstname': ['Adrian'], \
            'person.2.lastname': ['Holovaty']})
    >>> d
    {'person': {'1': {'lastname': ['Willison'], 'firstname': ['Simon']},
    '2': {'lastname': ['Holovaty'], 'firstname': ['Adrian']}}}
    >>> d['person']
    {'1': {'lastname': ['Willison'], 'firstname': ['Simon']},
    '2': {'lastname': ['Holovaty'], 'firstname': ['Adrian']}}
    >>> d['person']['1']
    {'lastname': ['Willison'], 'firstname': ['Simon']}

    # Gotcha: Results are unpredictable if the dots are "uneven":
    >>> DotExpandedDict({'c.1': 2, 'c.2': 3, 'c': 1})
    {'c': 1}
    """
    def __init__(self, key_to_list_mapping):
        for k, v in key_to_list_mapping.items():
            current = self
            bits = k.split('.')
            for bit in bits[:-1]:
                current = current.setdefault(bit, {})
            # Now assign value to current position
            try:
                current[bits[-1]] = v
            except TypeError:  # Special-case if current isn't a dict.
                current = {bits[-1]: v}

# ----------------- Random keys ----------------- #

BASE62_CONV = BaseConv(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz'
)


def gen_file_key():
    """Generates random file key.

    :return: File key, length is between 1 - 22 bytes.
    :rtype: ``str``
    """
    # 62**22 - 1 (full 22 base-62 digits) > 2**128
    n = random.randint(1, 62 ** 22 - 1)
    return BASE62_CONV.encode(n)


def gen_file_sub_key():
    """Generates random file sub key.

    :return: File sub key, length is between 1 - 5 bytes.
    :rtype: ``str``
    """
    n = random.randint(1, 62 ** 5 - 1)
    return BASE62_CONV.encode(n)


def gen_ocl_token():
    """Generates random ocl token.

    :return: token, length equals 30 bytes.
    :rtype: ``str``
    """
    return BASE62_CONV.encode(random.randint(62 ** 29 - 1, 62 ** 30 - 1))


# ----------------- Custom exception ----------------- #

class UnsupportedFileTypeError(Exception):
    def __init__(self, ext):
        self.ext = ext

    def __str__(self):
        return 'Files with extension "%s" are not supported.' % (self.ext,)


class CommandError(Exception):
    def __init__(self, cmd=None, code=None, stdout=None, stderr=None):
        self.cmd = cmd
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return 'Command [%s] has failed with code: %d' % (self.cmd, self.code)
