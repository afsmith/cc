from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.translation import ugettext_lazy as _

from . import tasks
from .services import get_message
from .forms import MessageForm
from .services import send_notification_email, edit_email_and_resend_message
from cc.apps.accounts.services import verify_ocl_token
from cc.apps.content.forms import FileImportForm
from cc.libs.exceptions import MessageExpired

from annoying.decorators import render_to, ajax_request


@ensure_csrf_cookie
@auth_decorators.login_required
@render_to('main/send_message.html')
def send_message(request):
    '''
    Send message view / Home view
    '''
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save()
            # save message owner
            message.owner = request.user
            message.save()
            # save signature of the owner
            request.user.signature = message_form.cleaned_data['signature']
            request.user.save()

            # process the PDF and send message
            tasks.process_file_and_send_message(message, request)

            return {'thankyou_page': True}
    else:
        message_form = MessageForm(initial={
            'message': (
                u'<br><br><br><br>'
                '[link]'
                '<br><br>'
                '<div id="signature">{}</div>'.format(request.user.signature)
            ),
            'signature': request.user.signature
        })

    return {
        'message_form': message_form,
        'import_file_form': FileImportForm(),
    }


@http_decorators.require_POST
@auth_decorators.login_required
@ajax_request
def resend_message(request):
    '''
    Resend the message
    '''
    try:
        message = get_message(request.POST.get('message_id'), request.user)
    except MessageExpired:
        return {
            'status': 'ERROR',
            'message': _(
                "This message's files are expired, please send a new one."
            )
        }
    else:
        edit_email_and_resend_message(request, message)
        return {
            'status': 'OK'
        }


@ensure_csrf_cookie
@render_to('main/view_message.html')
def view_message(request, message_id=None):
    token = request.GET.get('token')
    if token:
        ocl_token = verify_ocl_token(token)
        if not ocl_token:
            return {
                'ocl_expired': True
            }

        try:
            message = get_message(message_id, ocl_token.user)
        except MessageExpired:
            return {
                'message_expired': True
            }
        else:
            # check if owner is checking message
            is_owner_viewing = (ocl_token.user == message.owner)

            # there is only 1 file per message for now so return that file
            file = message.files.all()[0]

            # notify the sender if "notify when link clicked" option is on
            log = None
            if not is_owner_viewing:
                log = send_notification_email(2, message, ocl_token.user)

            return {
                'message': message,
                'file': file,
                'token': token,
                'ocl_user': ocl_token.user,
                'is_owner_viewing': is_owner_viewing,
                'tracking_log': log,
            }
    else:
        return redirect(reverse('auth_login'))
