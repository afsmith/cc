from django.views.generic import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators

from .models import Contact
from .forms import ContactForm
from cc.libs.utils import LoginRequiredMixin

from annoying.decorators import ajax_request, render_to
from os.path import splitext
import csv


class AddressBookListView(LoginRequiredMixin, CreateView):
    form_class = ContactForm
    template_name = 'address_book/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Contact.objects.filter(
            user=self.request.user
        ).order_by('work_email')
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
        'company',
    )[:20]

    return {
        'contacts': list(contacts)
    }


@auth_decorators.login_required
@render_to('address_book/import.html')
def import_contacts(request):
    errors = []
    if request.method == 'POST':
        f = request.FILES['file']
        if splitext(f.name)[1].lower() == '.csv':
            try:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        Contact.objects.get_or_create(
                            work_email=row.get('work_email', ''),
                            work_phone=row.get('work_phone', ''),
                            work_fax=row.get('work_fax', ''),
                            work_website=row.get('work_website', ''),
                            personal_email=row.get('personal_email', ''),
                            home_phone=row.get('home_phone', ''),
                            mobile_phone=row.get('mobile_phone', ''),
                            first_name=row.get('first_name', ''),
                            last_name=row.get('last_name', ''),
                            title=row.get('title', ''),
                            company=row.get('company', ''),
                            user=request.user,
                        )
                    except Exception as e:
                        errors.append(e.__str__())
            except:
                errors = ['The uploaded file is not csv file']
        else:
            errors = ['The uploaded file is not csv file']

    return {
        'errors': errors
    }
