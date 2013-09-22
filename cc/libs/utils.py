def get_domain(request):
    protocol = 'http'
    if request.is_secure():
        protocol = 'https'

    return '%s://%s' % (protocol, request.get_host())
