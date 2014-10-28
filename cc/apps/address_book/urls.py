from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cc.apps.address_book.views',
    url(r'^add/$',
        RegistrationView.as_view(form_class=UserCreationForm),
        name='accounts_register'),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        name='auth_login'),
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='auth_logout'),
)
