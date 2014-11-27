from django.views.generic import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators

from .models import Contact
from .forms import ContactForm
from cc.libs.utils import LoginRequiredMixin

from annoying.decorators import ajax_request


class AddressBookListView(LoginRequiredMixin, CreateView):
    form_class = ContactForm
    template_name = 'address_book/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Contact.objects.order_by('work_email')
        return super(AddressBookListView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('address_book_list')

    def get_initial(self):
        return {'user': self.request.user}


class AddressBookUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ContactForm
    template_name = 'address_book/update.html'
    model = Contact

    def get_success_url(self):
        return reverse('address_book_list')

    def get_initial(self):
        return {'user': self.request.user}


@auth_decorators.login_required
@ajax_request
def search_contacts(request):
    contacts = Contact.objects.search(
        request.GET.get('q')
    ).filter(user=request.user).values(
        'work_email',
        'first_name',
        'last_name',
        'id'
    )[:20]

    return {
        'contacts': list(contacts)
    }
