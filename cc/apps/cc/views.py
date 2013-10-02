from django.contrib.auth import decorators as auth_decorators

from cc.apps.cc_messages.models import Message

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('main/report.html')
def report(request):
    '''
    Reporting view
    '''
    return {
        'messages': Message.objects.filter(owner=request.user).order_by('created_at')
    }
