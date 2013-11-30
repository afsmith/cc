from mdetect import UAgentInfo
import datetime

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


def format_dbtime(time_from_db):
    if time_from_db is None:
        return '00:00:00'
    time_in_second = time_from_db / 10.0
    #return str(datetime.timedelta(seconds=time_in_second))
    m, s = divmod(time_in_second, 60)
    h, m = divmod(m, 60)
    return '{0:02.0f}:{1:02.0f}:{2:04.1f}'.format(h, m, s)