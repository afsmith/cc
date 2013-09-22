from django.contrib.auth import decorators as auth_decorators

from .services import create_ocl_and_send_mail
from cc.apps.content.forms import FileImportForm
from cc.apps.content.services import create_course_from_message
from cc.apps.cc_messages.forms import MessageForm

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('main/message.html')
def home(request):
    '''
    Home view
    '''
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save()
            message.owner = request.user
            message.save()
            course = create_course_from_message(message)
            create_ocl_and_send_mail(course, request, message)

            return {'thankyou_page': True}
    else:
        message_form = MessageForm()

    return {
        'message_form': message_form,
        'import_file_form': FileImportForm(),
    }
