from django.core.urlresolvers import reverse

from .models import OneClickLinkToken, Invitation

from templated_email import send_templated_mail
from datetime import date

from django.contrib.auth import login

from requests_oauthlib import OAuth2Session
from cc.apps.accounts.models import CUser
import jwt

def verify_ocl_token(token):
    try:
        ocl_token = OneClickLinkToken.objects.get(token=token)
    except OneClickLinkToken.DoesNotExist:
        return False
    if ocl_token.expires_on < date.today():
        return False
    return ocl_token


def send_invitation_email(invitation, domain):
    if invitation.status == Invitation.STATUS_SENT:
        link = '{}{}?invitation_code={}'.format(
            domain, reverse('accounts_register'), invitation.code
        )

        send_templated_mail(
            template_name='invitation',
            from_email=invitation.from_user.email,
            recipient_list=[invitation.to_email],
            context={
                'link': link,
            }
        )
    elif invitation.status == Invitation.STATUS_ACCEPTED:
        send_templated_mail(
            template_name='invitation_active',
            from_email=invitation.from_user.email,
            recipient_list=[invitation.to_email],
            context={}
        )

def get_authorization_url_sso(settings):
    CLIENT_ID = settings['CLIENT_ID']
    REDIRECT_URI = settings['REDIRECT_URI_LIVE']
    AUTHORIZATION_BASE_URL = settings['AUTHORIZATION_BASE_URL']
    RESOURCE_NAME = settings['RESOURCE_NAME']

    azure_session = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)    
    authorization_url, state = azure_session.authorization_url(AUTHORIZATION_BASE_URL % RESOURCE_NAME)
    return (authorization_url, state)    

def get_user_sso(settings, aad_code):
    BASE_TOKEN_URL = settings['BASE_TOKEN_URL']
    REDIRECT_URI = settings['REDIRECT_URI']
    CLIENT_ID = settings['CLIENT_ID']
    CLIENT_KEY = settings['CLIENT_KEY']
    RESOURCE_URI = settings['RESOURCE_URI']
    RESOURCE_NAME = settings['RESOURCE_NAME']
    
    azure_session = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    token_dict = azure_session.fetch_token(BASE_TOKEN_URL % RESOURCE_NAME, code=aad_code, client_secret=CLIENT_KEY, resource=RESOURCE_URI)
    
    if token_dict:        
        data = jwt.decode(token_dict['id_token'], verify=False)
        email = data['email']
        family_name = data['family_name']
        given_name = data['given_name']
        kwargs = dict(email=email, first_name=given_name, last_name=family_name)
        return CUser.objects.create_azure_user(**kwargs)
    
    return None