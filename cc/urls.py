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
    url(r'^report/$', 'cc.apps.cc.views.report', name='report'),
    url(r'^upload/$', 'cc.apps.content.views.upload_file', name='upload_file'),

    # registration
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=UserCreationForm)),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^accounts/', include('registration.backends.default.urls')),

    # apps
    url(r'^content/', include('cc.apps.content.urls')),

    # tracking email opened
    url(r'^track/(?P<course_id>\d+)/(?P<user_id>\d+)$',
        'cc.apps.cc.views.track_email', name='track_email'),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL
    if media_url.startswith('/'):
        media_url = media_url[1:]

    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % media_url,
            'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
    )
