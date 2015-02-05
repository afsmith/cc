from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.decorators import http as http_decorators
from django.contrib.auth import login
from django.conf import settings

from requests_oauthlib import OAuth2Session
from .models import Invitation
from .forms import InvitationForm
from .services import send_invitation_email, get_authorization_url_sso, get_user_sso
from cc.libs.utils import get_domain

from annoying.decorators import ajax_request
import requests

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

def login_sso(request):
    authorization_url, state = get_authorization_url_sso(settings.SSO)
    resp = requests.get(authorization_url)    
    
    return redirect(resp.url)

def token_sso(request):    
    aad_code = request.GET.get('code','')
    
    if aad_code:
        user = get_user_sso(settings.SSO, aad_code)
              
        if user is not None:                                
            login(request, user)
            return redirect('/')
    
    return redirect(reverse('auth_login'))
