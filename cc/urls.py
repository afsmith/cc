from django.conf.urls import patterns, include, url
from django.conf import settings

from cc.apps.accounts.forms import UserCreationForm
from registration.backends.default.views import RegistrationView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    # ----- CC APP  ----- #
    url(r'^$', 'cc.apps.cc.views.home', name='home'),
    url(r'^upload/$', 'cc.apps.content.views.upload_file', name='upload_file'),

    # registration
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=UserCreationForm)),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^accounts/', include('registration.backends.default.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
