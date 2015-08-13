from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.shortcuts import redirect
from cc.libs.utils import LoginRequiredMixin
from django.http import HttpResponse
from annoying.decorators import ajax_request, render_to
from cc import settings
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cc.apps.accounts.models import CUser
from cc.apps.address_book.models import Contact
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
import json
import jwt
from cc.apps.cc_messages.models import Message
from cc.apps.cc_messages import tasks
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from cc.apps.cc_messages.forms import UploadFileForm
from cc.apps.content.views import upload_file
from django.core.files import storage
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.http import HttpResponse
from contextlib import closing
from django.template.response import TemplateResponse
from  cc.apps.content.services import save_pdf
from  cc.apps.cc_messages.models import File
from datetime import timedelta
from cc.apps.reports import services
from cc.apps.reports.views import get_object_or_404, _format_data_for_chart
from django.core import serializers

BEARER = 'Bearer'
WHERE_IS_JSON = 'info'
LINK_TOKEN = '<br><div id="link_token">[link{}]</div>'
OPTIONS = {
        'verify_signature': False,
        'verify_exp': False,
        'verify_nbf': True,
        'verify_iat': True,
        'verify_aud': False,
        'require_exp': False,
        'require_iat': True,
        'require_nbf': True,
        }

@csrf_exempt
def sendemail(request):
     if request.path in  settings.OAUTH_TOKEN_REQUIRED_URLS:


          userAzureAd = validate_and_login(request)
          user = request.user


          if userAzureAd:
             try:

                json_data = get_json(request)

            
                del request.FILES[WHERE_IS_JSON]

                uploaded_files = upload_files(request)


             except Exception as e:
                  return HttpResponse(status=500,content= ('Error occured: {}'.format(e.__str__())))
             recipients = json_data['to']
             contacts =[]
             for recipient in recipients:

                 email = recipient['email']
                 firstname = recipient['firstname']
                 lastname = recipient['lastname']
                 crmContactId = recipient['crmContactId']
                 contact = add_or_update_contact(request,email,firstname,lastname,crmContactId)
                 contacts.append(contact)


             receivers = _fetch_receiver_ids(contacts,user)

             message_content = generateMessage(json_data['content'],uploaded_files)

             message = Message.objects.create(
                    subject = json_data['subject']  ,
                    cc_me =   json_data['ccSender']  ,
                    message = message_content  ,
                    allow_download = json_data['allowDownload'],
                    owner = user

                    )
             message.receivers = receivers
             message.files = uploaded_files
              # add expired_at
             message.expired_at = message.created_at + timedelta(days=settings.MESSAGE_EXPIRED_AFTER)
             message.save()

             # process the PDF and send message
             tasks.process_files_and_send_message(message, request)


             return HttpResponse(status=200,content=('{"knetoSendId":',message.pk,'}'))

     return HttpResponse(status=403,content='forbidden2')

def generateMessage(content,uploaded_files):
    index =0;
    for link_to_file in uploaded_files:
        index= index+1
        content = content + LINK_TOKEN.format(index)
    return content

def upload_files(request):
  ids_list =[]
  index = 0
  for file in request.FILES.values():


      def coping_file_callback(full_orig_file_path):
            with closing(
                storage.default_storage.open(full_orig_file_path, 'wb')
            ) as fh:
                for chunk in file.chunks():
                    fh.write(chunk)
      stored_pdf = save_pdf(
            request.user,
            file.name,
            coping_file_callback
        )
      if (stored_pdf['status'] == 'OK'):
           ids_list.append(stored_pdf['file_id'])

      #add link info to file
      try:
         f = File.objects.get(pk=int(stored_pdf['file_id']))
      except File.DoesNotExist:
         print 'File {} doesnt exist'.format(f)
         continue
      else:
         index +=1
         f.index = index
         f.link_text = file.name
         f.save()


  return ids_list


def get_json(request):
        file = request.FILES[WHERE_IS_JSON]
        data =''
        for chunk in file.chunks():
            data+=chunk
        json_data = json.loads(data)

        return json_data



def handle_uploaded_file(f):
    with open('d:\\ame.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def _fetch_receiver_ids(contacts, owner):
    receiver_list = []
    for contact in contacts:
        email = contact.work_email
        # look for user with same email
        user_qs = CUser.objects.filter(email__iexact=email)
        if user_qs:
           receiver_list.append(user_qs[0].id)
        else:  # otherwise create user
           user = CUser.objects.create_receiver_user(email)
           receiver_list.append(user.id)
    return receiver_list



@csrf_exempt
def addContact(request ):
    if request.path in  settings.OAUTH_TOKEN_REQUIRED_URLS:
          if validate_and_login(request):
             json_data = json.loads(request.body)
             email = json_data['email']
             firstname = json_data['firstname']
             lastname = json_data['lastname']
             crmContactId = json_data['crmContactId']

             contact = add_or_update_contact(request,email,firstname,lastname,crmContactId)

             return prepare_respone_contact(contact)


    return HttpResponse(status=403,content='forbidden')

def validate_and_login(request,create_user=True):
    httpAuth = request.META.get('HTTP_AUTHORIZATION', '')
    if  httpAuth!=None and httpAuth.startswith(BEARER):

        token = (httpAuth[len(BEARER)+1:])

        data = jwt.decode(token,   options=OPTIONS )
        if validate_data_in_token(data):
            userAzureAd = add_or_update_user_and_login(data, request,create_user)
            return userAzureAd

        else:
            return False


def add_or_update_user_and_login(data, request,create_user=True):
    kwargs = {}
    kwargs['email'] = kwargs['first_name'] = data['email']
    if 'given_name' in data:
        kwargs['first_name'] = data['given_name']
    if 'family_name' in data:
        kwargs['last_name'] = data['family_name']
    if create_user:
       userAzureAd = CUser.objects.create_azure_user(**kwargs)
    else:
       userAzureAd = CUser.objects.get(email=data['email'])

    if userAzureAd is not None:
        login(request, userAzureAd)
        return userAzureAd


def validate_data_in_token(data):
    if settings.SSO['CLIENT_ID']!=data['appid']:
        return False
    return True

def add_or_update_contact(request,email,firstname,lastname,crmContactId):
    if request.POST != None:

        user = request.user
        contact_updated = update_existing(email,firstname,lastname,crmContactId,user)
        if contact_updated:
            return contact_updated
        else:
            try:
               return Contact.objects.create(
                    work_email=  email ,
                    first_name= firstname ,
                    last_name= lastname ,
                    crmContactId= crmContactId ,
                    user=user,
                )
            except Exception as e:
                 print(('Error occured: {}'.format(e.__str__())))

def update_existing(email,firstname,lastname,crmContactId,user):

    try:
        contact = Contact.objects.get(crmContactId = crmContactId , user = user)
        contact.work_email =  email
        contact.first_name =  firstname
        contact.last_name=    lastname
        contact.save()

        return contact
    except Contact.DoesNotExist:
        return False



def prepare_respone_contact(contact):
    content='{"KnetoContactId"=',contact.id,'}'
    return HttpResponse(status=200,content = content)

@csrf_exempt
@ajax_request
def getreport(request,knetoSendId):
    userAzureAd = validate_and_login(request,create_user=False)

    knetoSendId =request.GET.get('knetoSendId', '')
    message_id = knetoSendId

    '''
    Reporting detail view
    '''
    this_message = get_object_or_404(Message, pk=message_id)
    services.check_permission(this_message, request.user)

    # # get all messages for dropdown
    all_messages = (
        Message.objects
        .filter(owner=request.user)
        .exclude(files=None)
        .order_by('created_at').reverse()
    )

    # get missing data
    missing_data = services.get_missing_data(this_message)

    # get recipient without tracking data
    uninterested_recipients = services.get_recipients_without_tracking_data(
        this_message, False
    )


    user_id = this_message.owner
    log = services.get_email_action_group_by_recipient(
        message_id, user_id
    )
    count = None
    last_open = None
    if log and log[0]['visit_count'] > 0:
        last_open = services.get_last_email_open(message_id, user_id)
        count =  log[0]['visit_count']

    json_data_out= {
        'this_message': this_message,
        'messages': all_messages,
        'missing_data': missing_data,
        'uninterested_recipients': uninterested_recipients,
        'count':count,
        'last_open': last_open
    }

    #data = serializers.serialize('json',json_data_out)

    return TemplateResponse(request, 'main/report_detail_api.html',   json_data_out  )



