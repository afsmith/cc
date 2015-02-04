from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.decorators import http as http_decorators
from django.contrib.auth import authenticate, login
from django.conf import settings

from requests_oauthlib import OAuth2Session
from .models import Invitation
from .forms import InvitationForm
from .services import send_invitation_email
from cc.libs.utils import get_domain
from cc.apps.accounts.models import CUser

from annoying.decorators import ajax_request
import requests
import jwt


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
    constants = settings.SSO
    CLIENT_ID = constants['CLIENT_ID']
    REDIRECT_URI = constants['REDIRECT_URI_LIVE']
    AUTHORIZATION_BASE_URL = constants['AUTHORIZATION_BASE_URL']
    RESOURCE_NAME = constants['RESOURCE_NAME']

    azure_session = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)    
    authorization_url, state = azure_session.authorization_url(AUTHORIZATION_BASE_URL % RESOURCE_NAME)
    resp = requests.get(authorization_url)    
    
    return redirect(resp.url)

def token_sso(request):
    constants = settings.SSO
    BASE_TOKEN_URL = constants['BASE_TOKEN_URL']
    REDIRECT_URI = constants['REDIRECT_URI']
    CLIENT_ID = constants['CLIENT_ID']
    CLIENT_KEY = constants['CLIENT_KEY']
    RESOURCE_URI = constants['RESOURCE_URI']
    RESOURCE_NAME = constants['RESOURCE_NAME']
    
    aad_code = request.GET.get('code','')
    
    azure_session = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    token_dict = azure_session.fetch_token(BASE_TOKEN_URL % RESOURCE_NAME, code=aad_code, client_secret=CLIENT_KEY, resource=RESOURCE_URI)
    
    if token_dict:        
        data = jwt.decode(token_dict['id_token'], verify=False)
        email = data['email']
        family_name = data['family_name']
        given_name = data['given_name']
        kwargs = dict(email=email, first_name=given_name, last_name=family_name)
        user = CUser.objects.create_azure_user(**kwargs)
                
        if user is not None:                                
            login(request, user)
            return redirect('/')
    return redirect(reverse('auth_login'))
