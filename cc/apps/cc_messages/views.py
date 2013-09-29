from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from .services import get_message
from cc.apps.accounts.services import verify_ocl_token
from cc.apps.cc.services import send_notification_email

from annoying.decorators import render_to


@render_to('main/view_message.html')
def view_message(request, id=None):
    token = request.GET.get('token')
    if token:
        ocl_token = verify_ocl_token(token)
        if not ocl_token:
            return {
                'ocl_expired': True
            }
        message = get_message(id, ocl_token.user)

        # there is only 1 file per message for now so return that file
        file = message.files.all()[0]
        pages_num = file.pages_num
        view_url = file.view_url
        page_list = []

        if pages_num == 1:
            page_list.append('%s/p.png' % view_url)
        elif pages_num > 1:
            for i in range(0, pages_num):
                page_list.append('%s/p-%d.png' % (view_url, i))

        # notify the sender if "notify when link clicked" option is on
        if message.notify_link_clicked:
            send_notification_email(message, ocl_token.user, 2)

        return {
            'message': message,
            'page_list': page_list,
            'token': token,
        }
    else:
        return redirect(reverse('home'))
