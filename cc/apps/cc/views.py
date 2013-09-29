from django import http
from django.conf import settings
from django.contrib.auth import decorators as auth_decorators

from . import tasks
from .services import notify_email_opened
from cc.apps.content.forms import FileImportForm
from cc.apps.cc_messages.forms import MessageForm

from annoying.decorators import render_to
from os import path


@auth_decorators.login_required
@render_to('main/send_message.html')
def home(request):
    '''
    Home view / Send message view
    '''
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save()
            message.owner = request.user
            message.save()
            tasks.process_file_and_send_message(message, request)

            return {'thankyou_page': True}
    else:
        message_form = MessageForm()

    return {
        'message_form': message_form,
        'import_file_form': FileImportForm(),
    }


def track_email(request, message_id, user_id):
    '''
    The 1x1 transparent image to track opened email
    '''
    # send email notification to owner of the message
    notify_email_opened(message_id, user_id)

    # serve the 1x1 transparent image
    img_abs_path = path.abspath(path.join(
        settings.STATICFILES_DIRS[0], 'img', 'transparent.gif'
    ))
    image_data = open(img_abs_path, 'rb').read()
    return http.HttpResponse(image_data, mimetype='image/gif')


@auth_decorators.login_required
@render_to('main/report.html')
def report(request):
    '''
    Reporting view
    '''
    return {}
