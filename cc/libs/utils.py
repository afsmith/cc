def get_domain(request):
    protocol = 'http'
    if request.is_secure():
        protocol = 'https'

    return '%s://%s' % (protocol, request.get_host())

def get_client_ip(request):
    address_list = request.META.get('HTTP_X_FORWARDED_FOR')
    if address_list:
        client_ip = address_list.split(',')[-1].strip()
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    return client_ip

def progress_formatter(progress):
    if progress == 0:
        return 0
    elif progress < 0.15:
        return 10
    elif progress > 0.85 and progress < 1:
        return 90
 
    return int(round(progress * 10) * 10)