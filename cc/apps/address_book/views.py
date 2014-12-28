from django.views.generic import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.shortcuts import redirect

from .models import Contact
from .forms import ContactForm, ImportContactForm
from cc.libs.utils import LoginRequiredMixin

from annoying.decorators import ajax_request, render_to


class AddressBookListView(LoginRequiredMixin, CreateView):
    form_class = ContactForm
    template_name = 'address_book/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('search')
        sort = self.request.GET.get('sort', '').split(',')
        contacts = Contact.objects
        if query:
            contacts = contacts.search(query)
        # get only from current user
        contacts = contacts.filter(user=self.request.user)

        ln, fn, em = 'last_name', 'first_name', 'work_email'
        if 'ln' in sort:
            ln = '-' + ln
        if 'fn' in sort:
            fn = '-' + fn
        if 'em' in sort:
            em = '-' + em
        contacts = contacts.order_by(ln, fn, em)

        kwargs['object_list'] = contacts
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
@http_decorators.require_POST
def delete_contact(request, pk):
    try:
        Contact.objects.get(pk=pk).delete()
    except:
        pass
    return redirect('address_book_list')


@auth_decorators.login_required
@ajax_request
def search_contacts(request):
    contacts = Contact.objects.search(
        request.GET.get('q')
    ).filter(user=request.user).values(
        'work_email',
        'first_name',
        'last_name',
        'company',
    )[:20]

    return {
        'contacts': list(contacts)
    }


@auth_decorators.login_required
@render_to('address_book/import.html')
def import_contacts(request):
    result = []
    if request.method == 'POST':
        form = ImportContactForm(request.POST, request.FILES)
        if form.is_valid():
            result = form.save(request.user)
    else:
        form = ImportContactForm()

    return {
        'form': form,
        'result': result
    }
