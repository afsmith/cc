from django.contrib.auth import decorators as auth_decorators

from cc.apps.content.forms import FileImportForm
from cc.apps.content.services import create_course
from cc.apps.cc_messages.forms import MessageForm
from cc.apps.accounts.services import create_group

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('cc/message.html')
def home(request):
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            print request.user
            message = message_form.save()
            message.owner = request.user
            message.save()
            group = create_group(message.receivers.all())
            create_course(message, group)

            # create OCL
            # send email

            return {'thankyou_page': True}
    else:
        message_form = MessageForm()

    return {
        'message_form': message_form,
        'import_file_form': FileImportForm(),
    }
