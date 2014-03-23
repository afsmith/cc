from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators

from .models import Invitation
from .forms import InvitationForm
from .services import send_invitation_email
from cc.libs.utils import get_domain

from annoying.decorators import ajax_request


@http_decorators.require_POST
@auth_decorators.login_required
@ajax_request
def invite(request):
    '''
    Invite user
    '''
    request_data = {}
    request_data['from_user'] = request.user.id
    request_data['to_email'] = request.POST.get('email')

    form = InvitationForm(request_data)
    if form.is_valid():
        inv = form.save()
        domain = get_domain(request)
        send_invitation_email(inv, domain)

        return {
            'status': 'OK',
        }
    else:
        return {
            'status': 'ERROR',
            'message': form.errors.get('to_email').as_text()
        }


@http_decorators.require_POST
@auth_decorators.login_required
@ajax_request
def remove_invitation(request, invitation_id):
    '''
    Remove invitation
    '''
    Invitation.objects.filter(pk=invitation_id).delete()
    return {}
